from datetime import datetime, timedelta
from jose import jwt
import bcrypt
from fastapi import HTTPException, status
from sqlalchemy import select
from src.domain.entities.user import User
from src.domain.entities.role import Role
from src.infrastructure.repositories.user_repository import UserRepository
from src.presentation.schemas.user import UserCreate
import os

SECRET_KEY = os.getenv("SECRET_KEY", "changethis_secret_key_for_dev_only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def get_password_hash(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def register_user(self, user_in: UserCreate) -> User:
        existing_user = await self.user_repo.get_by_username(user_in.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        hashed_pw = self.get_password_hash(user_in.password)
        new_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_pw
        )
        
        # Look up role dynamically
        role_stmt = select(Role).where(Role.name.ilike(user_in.role))
        result = await self.user_repo.session.execute(role_stmt)
        role = result.scalar_one_or_none()
        if role:
            new_user.roles = [role]
        else:
            default_role_stmt = select(Role).where(Role.name.ilike("user"))
            default_result = await self.user_repo.session.execute(default_role_stmt)
            default_role = default_result.scalar_one_or_none()
            if default_role:
                new_user.roles = [default_role]

        return await self.user_repo.create(new_user)

    async def authenticate_user(self, username: str, password: str) -> str:
        user = await self.user_repo.get_by_username(username)
        if not user or not self.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Aggregate permissions from all roles
        permissions_set = set()
        for role in user.roles:
            for perm in role.permissions:
                permissions_set.add(perm.slug)
        permissions_list = list(permissions_set)
        
        primary_role = user.roles[0].name if user.roles else "user"
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={
                "sub": str(user.id), 
                "role": primary_role,
                "permissions": permissions_list
            }, 
            expires_delta=access_token_expires
        )
        return access_token
