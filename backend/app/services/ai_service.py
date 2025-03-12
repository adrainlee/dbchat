import json
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

from app.models.database import DatabaseSchemaModel, AIQueryModel
from app.services.ai import (
    ChatMessage,
    create_ai_client,
    BaseAIClient,
    AIPromptBuilder
)

class AIService:
    """
    主AI服务类，整合AI客户端、提示构建器和数据库模式增强器
    提供SQL生成和通用聊天功能
    """
    
    def __init__(self):
        self.client: Optional[BaseAIClient] = None
        self.use_enhanced_prompts: bool = True  # 是否使用增强的提示词
    
    async def get_ai_sql_query(
        self,
        ai_model: str, 
        ai_service: str, 
        user_prompt: str, 
        db_schema: DatabaseSchemaModel,
        database_type: str
    ) -> AIQueryModel:
        """
        使用AI生成SQL查询
        
        参数:
            ai_model: AI模型名称
            ai_service: AI服务类型 (OpenAI, AzureOpenAI, Ollama)
            user_prompt: 用户的自然语言提示
            db_schema: 数据库模式
            database_type: 数据库类型
            
        返回:
            AIQueryModel: 包含生成的SQL查询和解释
        """
        # 确保有可用的客户端
        if not self.client:
            self.client = create_ai_client(ai_service, ai_model)
        
        # 选择提示构建方法
        if self.use_enhanced_prompts:
            system_prompt = AIPromptBuilder.build_sql_generation_prompt(db_schema, database_type)
        else:
            system_prompt = AIPromptBuilder.build_basic_sql_prompt(db_schema, database_type)
        
        # 准备消息
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
            raise HTTPException(
                status_code=500, 
                detail=f"无法将AI响应解析为SQL查询。AI响应为: {response_content}"
            )
    
    async def chat_prompt(
        self,
        prompt_messages: List[ChatMessage], 
        ai_model: str, 
        ai_service: str
    ) -> str:
        """
        发送通用聊天提示到AI服务
        
        参数:
            prompt_messages: 消息列表
            ai_model: AI模型
            ai_service: AI服务类型
            
        返回:
            str: AI的响应文本
        """
        if not self.client:
            self.client = create_ai_client(ai_service, ai_model)
            
        response = await self.client.complete_chat(prompt_messages)
        return response
    
    def set_use_enhanced_prompts(self, value: bool) -> None:
        """
        设置是否使用增强的提示词
        
        参数:
            value: True表示使用增强提示词，False使用基本提示词
        """
        self.use_enhanced_prompts = value
