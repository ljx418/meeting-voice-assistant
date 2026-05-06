"""
会议语音助手 - FastAPI 应用入口

提供语音识别、语义解析等后端服务
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api import router as api_router
from app.utils.logger import setup_logger

# 配置日志 - 统一输出到 logs 目录
import os
from pathlib import Path

# 日志目录
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志文件路径
LOG_FILE = LOG_DIR / "meeting.log"

# 配置日志
logger = setup_logger(
    name="meeting_voice",
    log_file=str(LOG_FILE),
    use_color=False  # 日志文件不使用彩色
)

# 创建 FastAPI 应用
app = FastAPI(
    title="Meeting Voice Assistant API",
    description="""
    会议语音助手后端 API

    ## 核心功能
    - 实时语音转文本 (WebSocket)
    - 会议信息提取 (说话人、角色、章节)
    - 会议记录导出

    ## 认证
    当前版本未启用认证，仅供本地开发使用
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置 CORS
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("Meeting Voice Assistant starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Meeting Voice Assistant shutting down...")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Meeting Voice Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/v1/test-write")
async def test_write():
    """测试文件写入"""
    import datetime
    from app.config import config
    test_dir = config.cache.cache_dir
    test_file = test_dir / f"test_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        test_file.write_text("test write at " + str(datetime.datetime.now()))
        return {"success": True, "file": str(test_file)}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
