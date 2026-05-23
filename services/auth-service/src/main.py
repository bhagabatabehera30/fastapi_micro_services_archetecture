from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.presentation.routers import auth
from src.core.dependencies import db
from packages.shared.database.core import Base
# Ensure models are imported so they are registered with Base metadata
from src.domain.entities.user import User
from src.domain.entities.role import Role
from src.domain.entities.permission import Permission
from src.domain.entities.association_tables import user_roles, role_permissions

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically create tables if they do not exist
    async with db._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed default permissions and roles
    async with db._session_factory() as session:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        import bcrypt

        perms_def = [
            {"name": "Trigger background jobs", "slug": "jobs.trigger", "module": "jobs"},
            {"name": "View customers", "slug": "customers.view", "module": "customers"},
            {"name": "Create customers", "slug": "customers.create", "module": "customers"},
            {"name": "Update customers", "slug": "customers.update", "module": "customers"},
            {"name": "Delete customers", "slug": "customers.delete", "module": "customers"}
        ]

        db_perms = {}
        for pd in perms_def:
            stmt = select(Permission).where(Permission.slug == pd["slug"])
            res = await session.execute(stmt)
            p_obj = res.scalar_one_or_none()
            if not p_obj:
                p_obj = Permission(name=pd["name"], slug=pd["slug"], module=pd["module"])
                session.add(p_obj)
            db_perms[pd["slug"]] = p_obj
        await session.flush()

        roles_def = ["admin", "user"]
        db_roles = {}
        for rname in roles_def:
            stmt = select(Role).options(selectinload(Role.permissions)).where(Role.name == rname)
            res = await session.execute(stmt)
            r_obj = res.scalar_one_or_none()
            if not r_obj:
                r_obj = Role(name=rname, description=f"Default {rname} role")
                if rname == "admin":
                    r_obj.permissions = list(db_perms.values())
                elif rname == "user":
                    r_obj.permissions = [db_perms["customers.view"]]
                session.add(r_obj)
            db_roles[rname] = r_obj
        await session.flush()

        # Check default superadmin
        stmt = select(User).options(selectinload(User.roles)).where(User.username == "superadmin")
        res = await session.execute(stmt)
        admin_user = res.scalar_one_or_none()
        if not admin_user:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), salt).decode('utf-8')
            admin_user = User(
                username="superadmin",
                email="admin@saas.com",
                hashed_password=hashed_password,
                is_active=True
            )
            admin_user.roles = [db_roles["admin"]]
            session.add(admin_user)

        await session.commit()
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
