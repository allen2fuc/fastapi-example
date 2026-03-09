from contextlib import asynccontextmanager
import logging
from typing import TypedDict
from fastapi import FastAPI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from .database import (
    close_database, 
    setup_database,
)
from .redis import (
    get_redis_client, 
    close_redis_client, 
)

from .logger import setup_logger

logger = logging.getLogger(__name__)


class State(TypedDict):
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]
    redis: Redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化日志
    setup_logger()

    logger.info("Starting Application Lifespan")

    # 初始化数据库
    engine, session_factory = await setup_database()

    # 初始化 Redis
    redis = await get_redis_client()

    yield State(engine=engine, session_factory=session_factory, redis=redis)

    # 关闭数据库
    await close_database(engine)

    # 关闭 Redis
    await close_redis_client(redis)

    logger.info("Application Lifespan Ended")