from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Database:
    def __init__(self, db_url: str):
        self._engine = create_async_engine(db_url, echo=False)
        self._session_factory = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine, class_=AsyncSession
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
