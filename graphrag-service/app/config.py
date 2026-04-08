from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GRAPHRAG_SERVICE_PORT: int = 8002
    LLM_PROVIDER: str = "dashscope"
    LLM_API_KEY: str = "sk-your-key-here"
    LLM_BASE_URL: str = "https://dashscope.aliyuncs.com"
    LLM_MODEL: str = "qwen-plus"
    GRAPHRAG_WORKSPACE: Path = Path("./rag_workspace")
    DEFAULT_TOP_K: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
