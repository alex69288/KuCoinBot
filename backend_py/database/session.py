from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from .config import Settings

def create_engine(settings: Settings):
    """Create async SQLAlchemy engine"""
    return create_async_engine(
        settings.database_url,
        echo=False,  # Set to True for SQL logging
        future=True,
    )

def create_session_factory(engine):
    """Create async session factory"""
    return sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

async def get_db_session(settings: Settings) -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)

    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

# Global engine for alembic
engine = None

async def init_db(settings: Settings):
    """Initialize database and create tables"""
    global engine
    engine = create_engine(settings)

    from .models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)