from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models.database import DatabaseSchemaModel

class IDatabaseService(ABC):
    """数据库服务接口，定义与数据库交互的通用方法"""
    
    @abstractmethod
    async def connect(self, connection_string: str) -> bool:
        """连接到数据库"""
        pass
    
    @abstractmethod
    async def test_connection(self, connection_string: str) -> bool:
        """测试数据库连接是否有效"""
        pass
    
    @abstractmethod
    async def get_database_schema(self) -> DatabaseSchemaModel:
        """获取数据库架构信息"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """执行SQL查询并返回结果"""
        pass
    
    @abstractmethod
    async def get_database_type(self) -> str:
        """获取数据库类型"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """关闭数据库连接"""
        pass