from typing import Dict, Optional, Type
from app.services.db_services.db_interface import IDatabaseService
from app.services.db_services.mysql_service import MySQLDatabaseService
from app.services.db_services.postgres_service import PostgreSQLDatabaseService
from app.services.db_services.sqlserver_service import SQLServerDatabaseService

class DatabaseManagerService:
    """数据库管理服务，负责选择合适的数据库服务实现"""
    
    def __init__(self):
        self.current_service: Optional[IDatabaseService] = None
        self.service_types: Dict[str, Type[IDatabaseService]] = {
            "mysql": MySQLDatabaseService,
            "postgres": PostgreSQLDatabaseService,
            "sqlserver": SQLServerDatabaseService,
        }
    
    def get_service_for_connection_string(self, connection_string: str) -> IDatabaseService:
        """根据连接字符串选择合适的数据库服务"""
        
        # 从连接字符串中检测数据库类型
        db_type = "unknown"
        if connection_string.startswith("mysql://"):
            db_type = "mysql"
        elif connection_string.startswith("postgresql://"):
            db_type = "postgres"
        elif connection_string.startswith("mssql://"):
            db_type = "sqlserver"
            
        # 如果找到匹配的服务类型，创建并返回实例
        if db_type in self.service_types:
            service_class = self.service_types[db_type]
            return service_class()
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")
    
    async def connect_to_database(self, connection_string: str) -> bool:
        """连接到数据库"""
        try:
            # 获取合适的服务
            self.current_service = self.get_service_for_connection_string(connection_string)
            
            # 连接到数据库
            success = await self.current_service.connect(connection_string)
            if not success:
                self.current_service = None
                
            return success
        except Exception as e:
            print(f"连接数据库错误: {str(e)}")
            self.current_service = None
            return False
    
    async def test_connection(self, connection_string: str) -> bool:
        """测试数据库连接"""
        try:
            service = self.get_service_for_connection_string(connection_string)
            return await service.test_connection(connection_string)
        except Exception as e:
            print(f"测试数据库连接错误: {str(e)}")
            return False
    
    def get_current_service(self) -> Optional[IDatabaseService]:
        """获取当前活动的数据库服务"""
        return self.current_service