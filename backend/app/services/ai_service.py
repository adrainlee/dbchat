from typing import List, Dict, Any, Optional, Union
import json
import aiohttp
from pydantic import BaseModel
from fastapi import HTTPException

from app.config import settings
from app.models.database import DatabaseSchemaModel, AIQueryModel

# 统一的聊天消息格式
class ChatMessage(BaseModel):
    role: str  # system, user, assistant
    content: str

# 抽象AI客户端接口
class BaseAIClient:
    async def complete_chat(self, messages: List[ChatMessage]) -> str:
        """发送消息到AI并获取响应"""
        raise NotImplementedError("子类必须实现此方法")

# OpenAI客户端实现
class OpenAIClient(BaseAIClient):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
    async def complete_chat(self, messages: List[ChatMessage]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, 
                                       detail=f"OpenAI API错误: {error_text}")
                
                data = await response.json()
                return data["choices"][0]["message"]["content"]

# Azure OpenAI客户端实现
class AzureOpenAIClient(BaseAIClient):
    def __init__(self, endpoint: str, api_key: str, model: str, api_version: str):
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model
        self.api_version = api_version
        self.api_url = f"{endpoint}/openai/deployments/{model}/chat/completions?api-version={api_version}"
        
    async def complete_chat(self, messages: List[ChatMessage]) -> str:
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, 
                                       detail=f"Azure OpenAI API错误: {error_text}")
                
                data = await response.json()
                return data["choices"][0]["message"]["content"]

# Ollama客户端实现
class OllamaClient(BaseAIClient):
    def __init__(self, endpoint: str, model: str):
        self.endpoint = endpoint
        self.model = model
        self.api_url = f"{endpoint}/api/chat"
        
    async def complete_chat(self, messages: List[ChatMessage]) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(status_code=response.status, 
                                       detail=f"Ollama API错误: {error_text}")
                
                data = await response.json()
                return data["message"]["content"]

# 主AI服务类
class AIService:
    def __init__(self):
        self.client = None
        
    def _create_client(self, ai_model: str, ai_service: str) -> BaseAIClient:
        """创建适合的AI客户端"""
        if ai_service == "OpenAI":
            if not settings.OPENAI_KEY:
                raise ValueError("缺少OpenAI API密钥")
            return OpenAIClient(api_key=settings.OPENAI_KEY, model=ai_model)
            
        elif ai_service == "AzureOpenAI":
            if not settings.AZURE_OPENAI_KEY or not settings.AZURE_OPENAI_ENDPOINT:
                raise ValueError("缺少Azure OpenAI凭据")
            return AzureOpenAIClient(
                endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_KEY,
                model=ai_model,
                api_version=settings.AZURE_OPENAI_VERSION
            )
            
        elif ai_service == "Ollama":
            if not settings.OLLAMA_ENDPOINT:
                raise ValueError("缺少Ollama端点")
            return OllamaClient(endpoint=settings.OLLAMA_ENDPOINT, model=ai_model)
            
        else:
            raise ValueError(f"不支持的AI服务: {ai_service}")
    
    async def get_ai_sql_query(self, 
                          ai_model: str, 
                          ai_service: str, 
                          user_prompt: str, 
                          db_schema: DatabaseSchemaModel,
                          database_type: str) -> AIQueryModel:
        """使用AI生成SQL查询"""
        if not self.client:
            self.client = self._create_client(ai_model, ai_service)
        
        # 构建提示
        system_prompt = f"""
你是一个有帮助的、友好的数据库助手。请不要回复与数据库或查询无关的任何信息。使用以下数据库模式创建你的答案：

{chr(10).join(db_schema.schema_raw)}

在查询结果中包含列名标题。
始终以以下JSON格式提供你的答案：
{{ "summary": "your-summary", "query": "your-query" }}

仅输出单行上的JSON格式。不要使用换行符。
在上述JSON响应中，将"your-query"替换为用于检索请求数据的数据库查询。
在上述JSON响应中，将"your-summary"替换为详细段落中创建此查询所采取的每个步骤的解释。
仅使用{database_type}语法进行数据库查询。
始终将SQL查询限制为{settings.MAX_ROWS}行。
始终包括所有表列和详细信息。
"""
        
        chat_messages = []
        
        # Ollama对系统提示支持有限，因此在使用Ollama时将系统提示作为用户提示
        if ai_service == "Ollama":
            chat_messages.append(ChatMessage(role="user", content=system_prompt))
        else:
            chat_messages.append(ChatMessage(role="system", content=system_prompt))
            
        chat_messages.append(ChatMessage(role="user", content=user_prompt))
        
        # 发送到AI服务
        response_content = await self.client.complete_chat(chat_messages)
        
        # 清理并解析响应
        cleaned_response = response_content.replace("```json", "").replace("```", "").replace("\\n", " ")
        
        try:
            # 解析JSON响应
            query_data = json.loads(cleaned_response)
            return AIQueryModel(summary=query_data["summary"], query=query_data["query"])
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, 
                             detail=f"无法将AI响应解析为SQL查询。AI响应为: {response_content}")
    
    async def chat_prompt(self, 
                     prompt_messages: List[ChatMessage], 
                     ai_model: str, 
                     ai_service: str) -> str:
        """发送通用聊天提示到AI服务"""
        if not self.client:
            self.client = self._create_client(ai_model, ai_service)
            
        response = await self.client.complete_chat(prompt_messages)
        return response