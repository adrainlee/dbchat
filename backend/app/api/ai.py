from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.models.database import DatabaseSchemaModel, AIQueryModel, AIConnectionModel
from app.services.ai_service import AIService, ChatMessage
from app.services.db_services.db_manager import DatabaseManagerService

router = APIRouter(prefix="/api/ai", tags=["ai"])

class AIPromptRequest(BaseModel):
    prompt: str
    ai_model: str
    ai_service: str

class ChatMessageRequest(BaseModel):
    messages: List[ChatMessage]
    ai_model: str
    ai_service: str

@router.post("/query")
async def generate_sql_query(
    request: AIPromptRequest, 
    ai_service: AIService = Depends(),
    db_manager: DatabaseManagerService = Depends()
):
    """生成SQL查询"""
    # 检查数据库连接
    db_service = db_manager.get_current_service()
    if not db_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未连接到数据库"
        )
    
    try:
        # 获取数据库架构
        db_schema = await db_service.get_database_schema()
        db_type = await db_service.get_database_type()
        
        # 生成SQL查询
        result = await ai_service.get_ai_sql_query(
            ai_model=request.ai_model,
            ai_service=request.ai_service,
            user_prompt=request.prompt,
            db_schema=db_schema,
            database_type=db_type
        )
        
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成SQL查询错误: {str(e)}"
        )

@router.post("/chat")
async def chat_with_ai(request: ChatMessageRequest, ai_service: AIService = Depends()):
    """与AI进行通用对话"""
    try:
        response = await ai_service.chat_prompt(
            prompt_messages=request.messages,
            ai_model=request.ai_model,
            ai_service=request.ai_service
        )
        
        return {"response": response}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI对话错误: {str(e)}"
        )

@router.get("/connections", response_model=List[AIConnectionModel])
async def get_ai_connections():
    """获取保存的AI连接配置"""
    # 注意：在实际实现中，这应该从数据库或配置中获取
    # 这里仅作为示例返回一些默认值
    return [
        AIConnectionModel(
            id=1,
            name="OpenAI GPT-4",
            service_type="OpenAI",
            model_name="gpt-4",
        ),
        AIConnectionModel(
            id=2,
            name="Azure OpenAI GPT-3.5",
            service_type="AzureOpenAI",
            model_name="gpt-35-turbo",
        ),
        AIConnectionModel(
            id=3,
            name="Ollama Llama2",
            service_type="Ollama",
            model_name="llama2",
        )
    ]