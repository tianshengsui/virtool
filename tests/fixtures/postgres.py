import pytest

from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession

from virtool.models import Base


@pytest.fixture(scope="function")
async def test_engine():
    engine = create_async_engine("postgresql+asyncpg://virtool:virtool@postgres/virtool", isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        try:
            await conn.execute(text("CREATE DATABASE test"))
        except ProgrammingError:
            pass
    return create_async_engine("postgresql+asyncpg://virtool:virtool@postgres/test")


@pytest.fixture(scope="function")
async def test_session(test_engine, loop):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session = AsyncSession(bind=test_engine)
    yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await session.close()
