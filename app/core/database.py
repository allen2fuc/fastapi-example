from typing import Tuple, cast
from fastapi import Request
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker

from .config import settings

async def setup_database() -> Tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:

    engine: AsyncEngine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO
    )

    session_factory = async_sessionmaker[AsyncSession](
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=settings.DATABASE_EXPIRE_ON_COMMIT
    )

    return engine, session_factory


async def close_database(engine: AsyncEngine):
    await engine.dispose()


async def get_session(request: Request) -> AsyncSession:
    session_factory = cast(
        async_sessionmaker[AsyncSession], 
        request.state.session_factory
    )

    async with session_factory() as session:
        yield session