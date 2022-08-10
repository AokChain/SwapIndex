from sqlmodel.ext.asyncio.session import AsyncSession
from .models import Settings
from sqlmodel import select
from . import db

async def init_settings():
    async with AsyncSession(db.async_engine) as session:
        statement = select(Settings)
        results = await session.exec(statement)

        if not results.first():
            settings = Settings()
            session.add(settings)

            await session.commit()
