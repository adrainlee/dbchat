import aiomysql
from typing import List, Dict, Any, Optional
from app.models.database import DatabaseSchemaModel, TableSchemaModel
from app.services.db_services.db_interface import IDatabaseService

class MySQLDatabaseService(IDatabaseService):
    """MySQL数据库服务实现"""
    
    def __init__(self):
        self.connection = None
        self.pool = None
        
    async def connect(self, connection_string: str) -> bool:
        """连接到MySQL数据库"""
        try:
            # 解析连接字符串
            # 格式: mysql://user:password@host:port/database
            parts = connection_string.replace("mysql://", "").split("@")
            user_pass = parts[0].split(":")
            host_port_db = parts[1].split("/")
            host_port = host_port_db[0].split(":")
            
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 3306
            db = host_port_db[1] if len(host_port_db) > 1 else ""
            
            # 创建连接池
            self.pool = await aiomysql.create_pool(
                host=host,
                port=port,
                user=user,
                password=password,
                db=db,
                autocommit=True
            )
            
            return True
        except Exception as e:
            print(f"MySQL连接错误: {str(e)}")
            return False
    
    async def test_connection(self, connection_string: str) -> bool:
        """测试MySQL数据库连接"""
        temp_pool = None
        try:
            # 解析连接字符串
            parts = connection_string.replace("mysql://", "").split("@")
            user_pass = parts[0].split(":")
            host_port_db = parts[1].split("/")
            host_port = host_port_db[0].split(":")
            
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 3306
            db = host_port_db[1] if len(host_port_db) > 1 else ""
            
            # 创建临时连接池
            temp_pool = await aiomysql.create_pool(
                host=host,
                port=port,
                user=user,
                password=password,
                db=db,
                autocommit=True
            )
            
            async with temp_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    
            return True
        except Exception as e:
            print(f"MySQL连接测试错误: {str(e)}")
            return False
        finally:
            if temp_pool:
                temp_pool.close()
                await temp_pool.wait_closed()
    
    async def get_database_schema(self) -> DatabaseSchemaModel:
        """获取MySQL数据库架构"""
        if not self.pool:
            raise ConnectionError("未连接到数据库")
        
        tables = []
        schema_raw = []
        db_name = ""
        
        async with self.pool.acquire() as conn:
            # 获取数据库名称
            async with conn.cursor() as cur:
                await cur.execute("SELECT DATABASE()")
                result = await cur.fetchone()
                db_name = result[0] if result else "unknown"
            
            # 获取表列表
            async with conn.cursor() as cur:
                await cur.execute("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = DATABASE()
                """)
                table_rows = await cur.fetchall()
                
                for table_row in table_rows:
                    table_name = table_row[0]
                    
                    # 获取表结构
                    await cur.execute(f"""
                        SELECT 
                            COLUMN_NAME, 
                            DATA_TYPE,
                            IS_NULLABLE,
                            COLUMN_KEY
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = DATABASE()
                        AND TABLE_NAME = '{table_name}'
                    """)
                    
                    columns = []
                    column_rows = await cur.fetchall()
                    
                    for col in column_rows:
                        column_name = col[0]
                        data_type = col[1]
                        is_nullable = col[2]
                        column_key = col[3]
                        
                        columns.append({
                            "name": column_name,
                            "type": data_type,
                            "nullable": is_nullable == "YES",
                            "key": column_key
                        })
                    
                    tables.append(TableSchemaModel(
                        name=table_name,
                        columns=columns
                    ))
                    
                    # 创建原始模式字符串
                    column_text = ", ".join([
                        f"{col['name']} {col['type']}{'NOT NULL' if not col['nullable'] else ''}{' PRIMARY KEY' if col['key'] == 'PRI' else ''}"
                        for col in columns
                    ])
                    schema_raw.append(f"CREATE TABLE {table_name} ({column_text});")
        
        return DatabaseSchemaModel(
            name=db_name,
            tables=tables,
            schema_raw=schema_raw
        )
    
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """执行SQL查询并返回结果"""
        if not self.pool:
            raise ConnectionError("未连接到数据库")
        
        results = []
        
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query)
                rows = await cur.fetchall()
                
                for row in rows:
                    results.append(dict(row))
        
        return results
    
    async def get_database_type(self) -> str:
        """获取数据库类型"""
        return "MySQL"
    
    async def close(self) -> None:
        """关闭数据库连接"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None