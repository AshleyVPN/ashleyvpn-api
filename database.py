from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Select

from config import DatabaseConfig


DATABASE_URL = f"postgresql+asyncpg://{DatabaseConfig.POSTGRES_USER}:{DatabaseConfig.POSTGRES_PASSWORD}@{DatabaseConfig.POSTGRES_DB_HOST}:{DatabaseConfig.POSTGRES_DB_PORT}/{DatabaseConfig.POSTGRES_DB}"

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def execute_query(query, scalars=True):
    async with async_session() as session:
        data = await session.execute(query)
        if not isinstance(query, Select):
            await session.commit()
        else:
            if scalars:
                data = data.scalars()
        return data
