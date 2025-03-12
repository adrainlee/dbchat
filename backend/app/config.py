import os
from pydantic import BaseSettings
from typing import Optional, Dict, Any, List

class Settings(BaseSettings):
    # 应用程序设置
    APP_NAME: str = "PY-DBChatPro"
    ENVIRONMENT_MODE: str = "local"  # local 或 hosted
    MAX_ROWS: int = 100  # 查询结果最大行数
    
    # 数据库设置
    DATABASE_URL: Optional[str] = None
    
    # AI服务设置
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_KEY: Optional[str] = None
    AZURE_OPENAI_VERSION: str = "2023-12-01-preview"
    OPENAI_KEY: Optional[str] = None
    OLLAMA_ENDPOINT: Optional[str] = None
    
    # Azure服务设置（用于hosted模式）
    AZURE_STORAGE_ENDPOINT: Optional[str] = None
    AZURE_KEYVAULT_ENDPOINT: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_TENANT_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# 创建全局设置实例
settings = Settings()