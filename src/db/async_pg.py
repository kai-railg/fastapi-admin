# -*- encoding: utf-8 -*-


from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.core import PG_URL

pg_async_engine =  create_async_engine(url=PG_URL)

pg_sessionmaker = sessionmaker(
    pg_async_engine,
    class_=AsyncSession
)

async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """session生成器 作为fastapi的Depends选项"""
    async with pg_sessionmaker() as session:
        yield session