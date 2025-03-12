from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

Base = declarative_base()

# Pydantic模型 - 用于API请求和响应
class TableSchemaModel(BaseModel):
    name: str
    columns: List[Dict[str, str]]
    
    class Config:
        orm_mode = True

class DatabaseSchemaModel(BaseModel):
    name: str
    tables: List[TableSchemaModel]
    schema_raw: List[str]
    
    class Config:
        orm_mode = True

class AIQueryModel(BaseModel):
    summary: str
    query: str
    
    class Config:
        orm_mode = True

class AIConnectionModel(BaseModel):
    id: Optional[int] = None
    name: str
    service_type: str  # AzureOpenAI, OpenAI, Ollama
    model_name: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    
    class Config:
        orm_mode = True

class HistoryItemModel(BaseModel):
    id: Optional[int] = None
    timestamp: datetime = datetime.now()
    prompt: str
    query: str
    summary: str
    
    class Config:
        orm_mode = True

# SQLAlchemy模型 - 用于数据库操作
class AIConnection(Base):
    __tablename__ = "ai_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    service_type = Column(String(50), nullable=False)
    model_name = Column(String(100), nullable=False)
    api_key = Column(String(255), nullable=True)
    endpoint = Column(String(255), nullable=True)

class HistoryItem(Base):
    __tablename__ = "history_items"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    prompt = Column(Text, nullable=False)
    query = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)