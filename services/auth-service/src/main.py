from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.presentation.routers import auth
from src.core.dependencies import db
from packages.shared.database.core import Base
# Ensure models are imported so they are registered with Base metadata
from src.domain.entities.user import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically create tables if they do not exist
    async with db._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="Auth Service API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/v1/auth/docs",
    openapi_url="/api/v1/auth/openapi.json"
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "auth-service"}
