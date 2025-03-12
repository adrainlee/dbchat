import aiohttp
from typing import List
from fastapi import HTTPException

from app.config import settings
from app.services.ai.ai_messages import ChatMessage

# 抽象AI客户端接口
class BaseAIClient:
    """
    AI客户端的抽象基类，定义与各种AI服务交互的接口
    """
    async def complete_chat(self, messages: List[ChatMessage]) -> str:
        """发送消息到AI并获取响应"""
        raise NotImplementedError("子类必须实现此方法")

# OpenAI客户端实现
class OpenAIClient(BaseAIClient):
    """
    OpenAI API的客户端实现
    """
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
    """
    Azure OpenAI API的客户端实现
    """
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
    """
    Ollama API的客户端实现
    """
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

# 客户端工厂函数
def create_ai_client(ai_service: str, ai_model: str) -> BaseAIClient:
    """
    根据服务类型和模型创建适当的AI客户端
    
    参数:
        ai_service: AI服务类型 ("OpenAI", "AzureOpenAI", "Ollama")
        ai_model: 模型名称
    
    返回:
        BaseAIClient: 创建的AI客户端实例
    """
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