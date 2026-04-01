"""
FunASR 说话人分离识别服务

独立的微服务，提供 HTTP API 进行带说话人分离的语音识别

启动:
    cd backend/funasr_service
    pip install -r requirements.txt
    python -m uvicorn main:app --host 0.0.0.0 --port 8001
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from funasr_service.api import router
from funasr_service.config import SERVICE_HOST, SERVICE_PORT

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("funasr_service")

app = FastAPI(
    title="FunASR Service",
    description="FunASR 说话人分离识别服务",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="", tags=["FunASR"])


@app.on_event("startup")
async def startup_event():
    logger.info(f"[FunASR Service] Starting on {SERVICE_HOST}:{SERVICE_PORT}")
    logger.info("[FunASR Service] Model will be loaded on first request")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("[FunASR Service] Shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=SERVICE_HOST,
        port=SERVICE_PORT,
        reload=False,
    )
