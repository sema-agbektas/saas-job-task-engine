
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
engine = create_async_engine(f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",echo=settings.DEBUG)
AsyncSessionFactory=sessionmaker(engine,class_=AsyncSession,expire_on_commit=False)
async def get_session():
    async with AsyncSessionFactory() as session:
        yield session