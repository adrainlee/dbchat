from pydantic import BaseModel
from typing import List

# 统一的聊天消息格式
class ChatMessage(BaseModel):
    """
    表示与AI模型交互的单个消息
    
    属性:
        role: 消息发送者的角色 (system, user, assistant)
        content: 消息内容
    """
    role: str  # system, user, assistant
    content: str