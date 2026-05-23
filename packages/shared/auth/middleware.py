from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel
import os

# We read the secret key from env, in a real app this could be configured via Vault or centralized config
SECRET_KEY = os.getenv("SECRET_KEY", "changethis_secret_key_for_dev_only")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class TokenData(BaseModel):
    user_id: int
    role: str
    permissions: list[str] = []

def get_current_token_data(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        role_str: str = payload.get("role", "user")
        permissions_list: list[str] = payload.get("permissions", [])
        if user_id_str is None:
            raise credentials_exception
        return TokenData(user_id=int(user_id_str), role=role_str, permissions=permissions_list)
    except (JWTError, ValueError):
        raise credentials_exception

def get_current_user_id(token_data: TokenData = Depends(get_current_token_data)) -> int:
    return token_data.user_id

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, token_data: TokenData = Depends(get_current_token_data)) -> TokenData:
        if token_data.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {self.allowed_roles}. Current role: {token_data.role}."
            )
        return token_data

class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, token_data: TokenData = Depends(get_current_token_data)) -> TokenData:
        if self.required_permission not in token_data.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required permission: '{self.required_permission}'"
            )
        return token_data
