from fastapi import APIRouter
from app.api.database import router as database_router
from app.api.ai import router as ai_router
from app.api.history import router as history_router

# 创建主路由
router = APIRouter()

# 包含所有子路由
router.include_router(database_router)
router.include_router(ai_router)
router.include_router(history_router)