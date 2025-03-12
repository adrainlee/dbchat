import asyncpg
from typing import List, Dict, Any, Optional
from app.models.database import DatabaseSchemaModel, TableSchemaModel
from app.services.db_services.db_interface import IDatabaseService

class PostgreSQLDatabaseService(IDatabaseService):
    """PostgreSQL数据库服务实现"""
    
    def __init__(self):
        self.connection = None
        self.pool = None
        self.current_db = None
        
    async def connect(self, connection_string: str) -> bool:
        """连接到PostgreSQL数据库"""
        try:
            # 解析连接字符串
            # 格式: postgresql://user:password@host:port/database
            parts = connection_string.replace("postgresql://", "").split("@")
            user_pass = parts[0].split(":")
            host_port_db = parts[1].split("/")
            host_port = host_port_db[0].split(":")
            
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 5432
            self.current_db = host_port_db[1] if len(host_port_db) > 1 else ""
            
            # 创建连接池
            self.pool = await asyncpg.create_pool(
                user=user,
                password=password,
                host=host,
                port=port,
                database=self.current_db
            )
            
            return True
        except Exception as e:
            print(f"PostgreSQL连接错误: {str(e)}")
            return False
    
    async def test_connection(self, connection_string: str) -> bool:
        """测试PostgreSQL数据库连接"""
        conn = None
        try:
            # 解析连接字符串
            parts = connection_string.replace("postgresql://", "").split("@")
            user_pass = parts[0].split(":")
            host_port_db = parts[1].split("/")
            host_port = host_port_db[0].split(":")
            
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 5432
            db = host_port_db[1] if len(host_port_db) > 1 else ""
            
            # 创建临时连接
            conn = await asyncpg.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=db
            )
            
            # 执行简单查询测试连接
            await conn.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"PostgreSQL连接测试错误: {str(e)}")
            return False
        finally:
            if conn:
                await conn.close()
    
    async def get_database_schema(self) -> DatabaseSchemaModel:
        """获取PostgreSQL数据库架构"""
        if not self.pool:
            raise ConnectionError("未连接到数据库")
        
        tables = []
        schema_raw = []
        
        async with self.pool.acquire() as conn:
            # 获取所有表名
            table_rows = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """)
            
            for table_row in table_rows:
                table_name = table_row['table_name']
                
                # 获取表结构
                column_rows = await conn.fetch("""
                    SELECT 
                        column_name, 
                        data_type,
                        is_nullable,
                        column_default,
                        (
                            SELECT 
                                CASE WHEN COUNT(*) > 0 THEN 'PRI' ELSE '' END
                            FROM 
                                information_schema.table_constraints tc
                            JOIN 
                                information_schema.constraint_column_usage ccu 
                                ON tc.constraint_name = ccu.constraint_name
                            WHERE 
                                tc.constraint_type = 'PRIMARY KEY' 
                                AND tc.table_name = c.table_name 
                                AND ccu.column_name = c.column_name
                        ) as key
                    FROM 
                        information_schema.columns c
                    WHERE 
                        table_schema = 'public' 
                        AND table_name = $1
                    ORDER BY 
                        ordinal_position
                """, table_name)
                
                columns = []
                columns_info = []
                
                for col in column_rows:
                    column_name = col['column_name']
                    data_type = col['data_type']
                    is_nullable = col['is_nullable']
                    default_value = col['column_default']
                    key = col['key']
                    
                    columns.append({
                        "name": column_name,
                        "type": data_type,
                        "nullable": is_nullable == "YES",
                        "key": key
                    })
                    
                    # 构建列信息字符串
                    column_str = f"{column_name} {data_type}"
                    if is_nullable == "NO":
                        column_str += " NOT NULL"
                    if default_value:
                        column_str += f" DEFAULT {default_value}"
                    if key == "PRI":
                        column_str += " PRIMARY KEY"
                    
                    columns_info.append(column_str)
                
                tables.append(TableSchemaModel(
                    name=table_name,
                    columns=columns
                ))
                
                # 创建原始模式字符串
                create_table_str = f"CREATE TABLE {table_name} (\n  "
                create_table_str += ",\n  ".join(columns_info)
                create_table_str += "\n);"
                schema_raw.append(create_table_str)
        
        return DatabaseSchemaModel(
            name=self.current_db,
            tables=tables,
            schema_raw=schema_raw
        )
    
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """执行SQL查询并返回结果"""
        if not self.pool:
            raise ConnectionError("未连接到数据库")
        
        results = []
        
        async with self.pool.acquire() as conn:
            try:
                # 针对SELECT查询
                if query.strip().upper().startswith("SELECT"):
                    rows = await conn.fetch(query)
                    
                    for row in rows:
                        results.append(dict(row))
                # 针对非SELECT查询（INSERT, UPDATE, DELETE等）
                else:
                    await conn.execute(query)
                    return [{"affected_rows": "Query executed successfully"}]
            except Exception as e:
                raise Exception(f"执行查询错误: {str(e)}")
        
        return results
    
    async def get_database_type(self) -> str:
        """获取数据库类型"""
        return "PostgreSQL"
    
    async def close(self) -> None:
        """关闭数据库连接"""
        if self.pool:
            await self.pool.close()
            self.pool = None