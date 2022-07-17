from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.ext.asyncio.session import AsyncEngine
from sqlmodel import create_engine, SQLModel
import config

async_engine = AsyncEngine(create_engine(config.sqlite_path_async, echo=False))

async def get_async_session() -> AsyncSession:
    async with AsyncSession(async_engine) as session:
        yield session

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)