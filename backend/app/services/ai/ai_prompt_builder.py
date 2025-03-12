from app.config import settings
from app.models.database import DatabaseSchemaModel
from app.services.ai.db_schema_enhancer import DatabaseSchemaEnhancer

class AIPromptBuilder:
    """
    负责构建和优化提示词的类
    """
    
    @staticmethod
    def build_sql_generation_prompt(db_schema: DatabaseSchemaModel, database_type: str) -> str:
        """
        构建用于SQL生成的增强提示
        
        参数:
            db_schema: 数据库模式
            database_type: 数据库类型
            
        返回:
            str: 优化的提示词
        """
        # 获取原始模式信息
        schema_raw = chr(10).join(db_schema.schema_raw)
        
        # 获取增强的数据库理解信息
        enhanced_understanding = DatabaseSchemaEnhancer.enhance_schema(db_schema, database_type)
        
        # 构建完整的增强提示
        prompt = f"""
你是一个专业的{database_type}数据库专家和SQL大师。请根据用户的自然语言描述，生成精确、高效的SQL查询。

## 数据库模式定义:
```sql
{schema_raw}
```

## 增强的数据库理解:
{enhanced_understanding}

## 查询生成指南:
1. 仔细分析用户的需求，确保理解他们真正想要的数据
2. 选择适当的表和字段，考虑上面描述的表关系
3. 使用正确的JOIN类型（INNER, LEFT, RIGHT）连接相关表
4. 添加WHERE子句筛选出精确匹配用户需求的数据
5. 正确处理NULL值和边缘情况
6. 使用适当的ORDER BY子句排序结果
7. 使用LIMIT {settings.MAX_ROWS} 限制结果数量
8. 确保使用{database_type}特有的SQL语法

在查询结果中包含列名标题。
始终以以下JSON格式提供你的答案：
{{ "summary": "your-summary", "query": "your-query" }}

仅输出单行上的JSON格式。不要使用换行符。
在上述JSON响应中，将"your-query"替换为用于检索请求数据的数据库查询。
在上述JSON响应中，将"your-summary"替换为详细段落中创建此查询所采取的每个步骤的解释。
"""
        
        return prompt
    
    @staticmethod
    def build_basic_sql_prompt(db_schema: DatabaseSchemaModel, database_type: str) -> str:
        """
        构建基本的SQL生成提示（不包含增强信息）
        
        参数:
            db_schema: 数据库模式
            database_type: 数据库类型
            
        返回:
            str: 基本提示词
        """
        # 使用原始模式
        schema_raw = chr(10).join(db_schema.schema_raw)
        
        # 构建基本提示
        prompt = f"""
你是一个有帮助的、友好的数据库助手。请不要回复与数据库或查询无关的任何信息。使用以下数据库模式创建你的答案：

{schema_raw}

在查询结果中包含列名标题。
始终以以下JSON格式提供你的答案：
{{ "summary": "your-summary", "query": "your-query" }}

仅输出单行上的JSON格式。不要使用换行符。
在上述JSON响应中，将"your-query"替换为用于检索请求数据的数据库查询。
在上述JSON响应中，将"your-summary"替换为详细段落中创建此查询所采取的每个步骤的解释。
仅使用{database_type}语法进行数据库查询。
始终将SQL查询限制为{settings.MAX_ROWS}行。
始终包括所有表列和详细信息。
"""
        
        return prompt