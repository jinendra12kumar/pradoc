import redis.asyncio as aioredis
from core.config import settings

_redis_client: aioredis.Redis | None = None


async def init_redis() -> aioredis.Redis:
    global _redis_client
    _redis_client = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
    )
    # Test connection
    await _redis_client.ping()
    return _redis_client


async def get_redis() -> aioredis.Redis:
    if _redis_client is None:
        raise RuntimeError("Redis client not initialised. Call init_redis() first.")
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
