from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from app.models.database import DatabaseSchemaModel
from app.services.db_services.db_manager import DatabaseManagerService

router = APIRouter(prefix="/api/database", tags=["database"])

@router.post("/connect")
async def connect_to_database(connection_string: str, db_manager: DatabaseManagerService = Depends()):
    """连接到数据库"""
    success = await db_manager.connect_to_database(connection_string)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法连接到数据库，请检查连接字符串"
        )
    
    return {"message": "成功连接到数据库"}

@router.post("/test")
async def test_database_connection(connection_string: str, db_manager: DatabaseManagerService = Depends()):
    """测试数据库连接"""
    success = await db_manager.test_connection(connection_string)
    
    return {"success": success}

@router.get("/schema")
async def get_database_schema(db_manager: DatabaseManagerService = Depends()):
    """获取数据库架构"""
    service = db_manager.get_current_service()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未连接到数据库"
        )
    
    try:
        schema = await service.get_database_schema()
        return schema
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据库架构错误: {str(e)}"
        )

@router.post("/execute")
async def execute_query(query: str, db_manager: DatabaseManagerService = Depends()):
    """执行SQL查询"""
    service = db_manager.get_current_service()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未连接到数据库"
        )
    
    try:
        results = await service.execute_query(query)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"执行查询错误: {str(e)}"
        )