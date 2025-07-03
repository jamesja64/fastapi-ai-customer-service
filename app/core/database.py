from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis
from app.core.config import settings

# 創建異步資料庫引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# 創建異步會話工廠
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 創建基礎模型類
Base = declarative_base()

# Redis 連接
redis_client = None


async def get_redis():
    """獲取 Redis 連接"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client


async def get_db():
    """獲取資料庫會話"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化資料庫"""
    async with engine.begin() as conn:
        # 創建所有表
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """關閉資料庫連接"""
    await engine.dispose()
    if redis_client:
        await redis_client.close()
