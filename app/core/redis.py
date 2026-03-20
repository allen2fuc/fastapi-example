from typing import cast
from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from .config import settings

redis_client = Redis.from_url(settings.REDIS_URL)

async def get_redis_client() -> Redis:
    return redis_client

async def close_redis_client(redis_client: Redis):
    await redis_client.close()


async def get_redis(request: Request) -> Redis:
    return cast(Redis, request.state.redis)


def rate_limit(max_attempts: int, window: int, key_prefix: str = "rate"):
    """
    限流依赖工厂。
    max_attempts: 窗口内最大请求次数
    window: 时间窗口（秒）
    key_prefix: Redis key 前缀
    """
    async def dependency(request: Request, redis: Redis = Depends(get_redis)):
        key = f"{key_prefix}:{request.client.host}"
        attempts = await redis.get(key)
        if attempts and int(attempts) >= max_attempts:
            ttl = await redis.ttl(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"请求过于频繁，请 {ttl} 秒后再试",
            )
        request.state.rate_limit_key = key
        request.state.rate_limit_window = window

    return Depends(dependency)


async def rate_limit_incr(request: Request, redis: Redis):
    """记录一次失败，刷新 TTL。"""
    key = request.state.rate_limit_key
    window = request.state.rate_limit_window
    await redis.incr(key)
    await redis.expire(key, window)


async def rate_limit_reset(request: Request, redis: Redis):
    """成功后清除计数。"""
    await redis.delete(request.state.rate_limit_key)