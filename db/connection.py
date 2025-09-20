from typing import Any, AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from config import settings


def create_engine() ->AsyncEngine:
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,  # 显示SQL语句
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
    )

    return engine

class SessionCreatError(Exception):
    def __init__(self, message: str = "Session creation failed") -> None:
        self.message = f"Session creation failed: {message}"
        super().__init__(self.message)

@asynccontextmanager
async def get_session(engine) -> AsyncGenerator[AsyncSession, Any]:
    async with AsyncSession(engine) as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise SessionCreatError(str(e))
