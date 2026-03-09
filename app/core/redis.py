from typing import cast
from fastapi import Request
from redis.asyncio import Redis

from .config import settings

redis_client = Redis.from_url(settings.REDIS_URL)

async def get_redis_client() -> Redis:
    return redis_client

async def close_redis_client(redis_client: Redis):
    await redis_client.close()


async def get_redis(request: Request) -> Redis:
    redis = cast(
        Redis, 
        request.state.redis
    )

    return redis