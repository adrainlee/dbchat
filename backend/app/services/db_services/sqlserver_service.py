import aioodbc
import pyodbc
from typing import List, Dict, Any, Optional
from app.models.database import DatabaseSchemaModel, TableSchemaModel
from app.services.db_services.db_interface import IDatabaseService

class SQLServerDatabaseService(IDatabaseService):
    """SQL Server数据库服务实现"""
    
    def __init__(self):
        self.connection = None
        self.pool = None
        self.dsn = None
        self.current_db = None
        
    async def connect(self, connection_string: str) -> bool:
        """连接到SQL Server数据库"""
        try:
            # 解析连接字符串
            # 格式: mssql://user:password@host:port/database
            parts = connection_string.replace("mssql://", "").split("@")
            user_pass = parts[0].split(":")
            host_port_db = parts[1].split("/")
            host_port = host_port_db[0].split(":")
            
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            host = host_port[0]
            port = host_port[1] if len(host_port) > 1 else "1433"
            self.current_db = host_port_db[1] if len(host_port_db) > 1 else ""
            
            # 创建ODBC连接字符串
            self.dsn = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host},{port};DATABASE={self.current_db};UID={user};PWD={password}"
            
            # 创建连接池
            self.pool = await aioodbc.create_pool(dsn=self.dsn, autocommit=True)
            
            return True
        except Exception as e:
            print(f"SQL Server连接错误: {str(e)}")
            return False
    
    async def test_connection(self, connection_string: str) -> bool:
        """测试SQL Server数据库连接"""
        temp_pool = None
        conn = None
        try:
            # 解析连接字符串
            parts = connection_string.replace("mssql://", "").split("@")
            user_pass = parts[0].split(":")
            host_port_db = parts[1].split("/")
            host_port = host_port_db[0].split(":")
            
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            host = host_port[0]
            port = host_port[1] if len(host_port) > 1 else "1433"
            db = host_port_db[1] if len(host_port_db) > 1 else ""
            
            # 创建ODBC连接字符串
            dsn = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host},{port};DATABASE={db};UID={user};PWD={password}"
            
            # 创建临时连接
            temp_pool = await aioodbc.create_pool(dsn=dsn, autocommit=True)
            async with temp_pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    await cur.fetchall()
            
            return True
        except Exception as e:
            print(f"SQL Server连接测试错误: {str(e)}")
            return False
        finally:
            if temp_pool:
                temp_pool.close()
    
    async def get_database_schema(self) -> DatabaseSchemaModel:
        """获取SQL Server数据库架构"""
        if not self.pool:
            raise ConnectionError("未连接到数据库")
        
        tables = []
        schema_raw = []
        
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                # 获取所有用户表名
                await cur.execute("""
                    SELECT 
                        TABLE_NAME 
                    FROM 
                        INFORMATION_SCHEMA.TABLES 
                    WHERE 
                        TABLE_TYPE = 'BASE TABLE' 
                        AND TABLE_CATALOG = ?
                """, self.current_db)
                
                table_rows = await cur.fetchall()
                
                for table_row in table_rows:
                    table_name = table_row[0]
                    
                    # 获取表结构
                    await cur.execute("""
                        SELECT 
                            c.COLUMN_NAME, 
                            c.DATA_TYPE,
                            c.CHARACTER_MAXIMUM_LENGTH,
                            c.IS_NULLABLE,
                            c.COLUMN_DEFAULT,
                            CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 'PRI' ELSE '' END AS COLUMN_KEY
                        FROM 
                            INFORMATION_SCHEMA.COLUMNS c
                        LEFT JOIN (
                            SELECT 
                                ku.TABLE_CATALOG,
                                ku.TABLE_SCHEMA,
                                ku.TABLE_NAME,
                                ku.COLUMN_NAME
                            FROM 
                                INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS tc
                            JOIN 
                                INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS ku
                                ON tc.CONSTRAINT_TYPE = 'PRIMARY KEY' 
                                AND tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
                        ) pk
                        ON 
                            c.TABLE_CATALOG = pk.TABLE_CATALOG
                            AND c.TABLE_SCHEMA = pk.TABLE_SCHEMA
                            AND c.TABLE_NAME = pk.TABLE_NAME
                            AND c.COLUMN_NAME = pk.COLUMN_NAME
                        WHERE 
                            c.TABLE_NAME = ? 
                            AND c.TABLE_CATALOG = ?
                        ORDER BY 
                            c.ORDINAL_POSITION
                    """, table_name, self.current_db)
                    
                    column_rows = await cur.fetchall()
                    
                    columns = []
                    columns_info = []
                    
                    for col in column_rows:
                        column_name = col[0]
                        data_type = col[1]
                        max_length = col[2]
                        is_nullable = col[3]
                        default_value = col[4]
                        key = col[5]
                        
                        # 如果数据类型是字符串类型且有最大长度
                        if max_length and data_type.lower() in ('char', 'varchar', 'nchar', 'nvarchar'):
                            data_type_full = f"{data_type}({max_length if max_length != -1 else 'MAX'})"
                        else:
                            data_type_full = data_type
                        
                        columns.append({
                            "name": column_name,
                            "type": data_type_full,
                            "nullable": is_nullable == "YES",
                            "key": key
                        })
                        
                        # 构建列信息字符串
                        column_str = f"{column_name} {data_type_full}"
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
            async with conn.cursor() as cur:
                try:
                    await cur.execute(query)
                    
                    # 针对SELECT查询
                    if query.strip().upper().startswith("SELECT"):
                        rows = await cur.fetchall()
                        
                        # 获取列名
                        columns = [column[0] for column in cur.description]
                        
                        # 构建结果字典
                        for row in rows:
                            result = {}
                            for i, value in enumerate(row):
                                result[columns[i]] = value
                            results.append(result)
                    # 针对非SELECT查询
                    else:
                        rowcount = cur.rowcount
                        return [{"affected_rows": rowcount}]
                except Exception as e:
                    raise Exception(f"执行查询错误: {str(e)}")
        
        return results
    
    async def get_database_type(self) -> str:
        """获取数据库类型"""
        return "SQL Server"
    
    async def close(self) -> None:
        """关闭数据库连接"""
        if self.pool:
            self.pool.close()
            self.pool = None