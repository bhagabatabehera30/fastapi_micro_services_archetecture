import os
from packages.shared.database.core import Database

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/app_db")
db = Database(DATABASE_URL)

async def get_db_session():
    async for session in db.get_session():
        yield session
