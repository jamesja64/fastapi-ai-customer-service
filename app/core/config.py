from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
import os


class Settings(BaseSettings):
    """應用配置設定"""
    
    # 基本配置
    PROJECT_NAME: str = "FastAPI AI Customer Service Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服務器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 資料庫配置
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT 配置
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Ollama AI 配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:14b"
    OLLAMA_TIMEOUT: int = 30
    
    # Elasticsearch 配置
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX: str = "knowledge_base"
    
    # CORS 配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # 安全配置
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # 日誌配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # 文件上傳配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # 緩存配置
    CACHE_TTL: int = 3600  # 1 hour
    
    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = 60
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 創建全局設定實例
settings = Settings()


# 資料庫配置
class DatabaseConfig:
    """資料庫相關配置"""
    
    @staticmethod
    def get_database_url() -> str:
        return settings.DATABASE_URL
    
    @staticmethod
    def get_redis_url() -> str:
        return settings.REDIS_URL


# AI 模型配置
class AIConfig:
    """AI 模型相關配置"""
    
    @staticmethod
    def get_ollama_config() -> dict:
        return {
            "base_url": settings.OLLAMA_BASE_URL,
            "model": settings.OLLAMA_MODEL,
            "timeout": settings.OLLAMA_TIMEOUT
        }


# 安全配置
class SecurityConfig:
    """安全相關配置"""
    
    @staticmethod
    def get_jwt_config() -> dict:
        return {
            "secret_key": settings.SECRET_KEY,
            "algorithm": settings.ALGORITHM,
            "expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
        }
