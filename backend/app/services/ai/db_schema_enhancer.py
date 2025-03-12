from typing import List, Dict, Any
from app.models.database import DatabaseSchemaModel, TableSchemaModel

class DatabaseSchemaEnhancer:
    """
    增强数据库模式信息，以帮助AI更好地理解数据库结构
    """
    
    @staticmethod
    def enhance_schema(db_schema: DatabaseSchemaModel, database_type: str) -> str:
        """
        分析数据库模式并生成增强的描述信息
        
        参数:
            db_schema: 包含表和列信息的数据库模式
            database_type: 数据库类型 (MySQL, PostgreSQL, SQL Server)
            
        返回:
            str: 增强的数据库描述
        """
        # 创建结构化的数据库描述
        enhanced_info = []
        
        # 1. 数据库概览
        db_overview = f"数据库 '{db_schema.name}' 包含 {len(db_schema.tables)} 个表。"
        enhanced_info.append(db_overview)
        
        # 2. 表和列的详细描述
        enhanced_info.append("\n## 详细的表结构:")
        
        for table in db_schema.tables:
            table_desc = f"\n### 表: {table.name}"
            enhanced_info.append(table_desc)
            
            # 列出主键
            primary_keys = [col for col in table.columns if col.get("key") == "PRI"]
            if primary_keys:
                pk_names = [pk["name"] for pk in primary_keys]
                enhanced_info.append(f"主键: {', '.join(pk_names)}")
            
            # 列出所有列及其属性
            enhanced_info.append("列:")
            for column in table.columns:
                nullable = "可为空" if column.get("nullable", True) else "非空"
                key_info = "主键" if column.get("key") == "PRI" else ""
                col_desc = f"- {column['name']}: {column['type']}, {nullable} {key_info}"
                enhanced_info.append(col_desc)
        
        # 3. 检测潜在表关系
        enhanced_info.append("\n## 可能的表关系:")
        relationships = DatabaseSchemaEnhancer._detect_relationships(db_schema.tables)
        
        if relationships:
            for rel in relationships:
                enhanced_info.append(f"- {rel}")
        else:
            enhanced_info.append("- 未检测到明显的表关系")
        
        # 4. 根据数据库类型添加特定建议
        enhanced_info.append(f"\n## {database_type}特定建议:")
        
        if database_type == "MySQL":
            enhanced_info.append("- 使用JOIN语句时考虑索引效率")
            enhanced_info.append("- 大型结果集考虑使用LIMIT和分页")
            enhanced_info.append("- 复杂查询考虑使用临时表或子查询")
        elif database_type == "PostgreSQL":
            enhanced_info.append("- 可以使用WITH子句(CTE)简化复杂查询")
            enhanced_info.append("- 考虑使用JSONB功能处理复杂数据")
            enhanced_info.append("- 可以利用Window函数进行高级分析")
        elif database_type == "SQL Server":
            enhanced_info.append("- 考虑使用TOP代替LIMIT")
            enhanced_info.append("- 复杂查询可使用CTE增加可读性")
            enhanced_info.append("- 使用适当的JOINS类型优化性能")
        
        # 5. SQL查询最佳实践
        enhanced_info.append("\n## SQL查询最佳实践:")
        enhanced_info.append("- 使用列的全名（表名.列名）以避免歧义")
        enhanced_info.append("- 添加适当的WHERE条件以限制结果集")
        enhanced_info.append("- 使用适当的联接类型（INNER JOIN、LEFT JOIN等）")
        enhanced_info.append("- 考虑结果的排序和分组")
        enhanced_info.append("- 避免SELECT *，明确指定需要的列")
        
        # 组合成最终的增强信息
        return "\n".join(enhanced_info)
    
    @staticmethod
    def _detect_relationships(tables: List[TableSchemaModel]) -> List[str]:
        """
        检测表之间可能存在的关系
        
        参数:
            tables: 表模型列表
            
        返回:
            List[str]: 检测到的表关系描述列表
        """
        relationships = []
        
        for table1 in tables:
            for table2 in tables:
                if table1.name != table2.name:
                    # 检查外键关系（基于命名约定）
                    for col1 in table1.columns:
                        col1_name = col1["name"].lower()
                        
                        # 检查是否有表名_id模式的列
                        if col1_name == f"{table2.name.lower()}_id":
                            relationships.append(f"{table1.name}.{col1['name']} 可能引用 {table2.name} 表的主键")
                        
                        # 检查列名与其他表主键匹配的情况
                        for col2 in table2.columns:
                            if col2.get("key") == "PRI" and col1_name == col2["name"].lower():
                                relationships.append(f"{table1.name}.{col1['name']} 可能引用 {table2.name}.{col2['name']}")
                                
                        # 检查是否包含表名（如customer_name可能关联到customers表）
                        if table2.name.lower() in col1_name and not col1_name.endswith('_id'):
                            relationships.append(f"{table1.name}.{col1['name']} 可能与 {table2.name} 表有关联")
        
        return list(set(relationships))  # 去重