from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.api import router as api_router
from app.services.db_services.db_manager import DatabaseManagerService
from app.services.ai_service import AIService

# 应用启动和关闭事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行的代码
    print(f"启动 {settings.APP_NAME} 应用...")
    yield
    # 应用关闭时执行的代码
    print(f"关闭 {settings.APP_NAME} 应用...")

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description="数据库AI助手API",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖注入
def get_db_manager():
    return DatabaseManagerService()

def get_ai_service():
    return AIService()

# 注册路由
app.include_router(api_router)

# 根路由
@app.get("/")
async def root():
    return {"message": f"欢迎使用 {settings.APP_NAME} API"}

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": f"发生错误: {str(exc)}"}
    )

# 直接运行此文件时启动应用
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)