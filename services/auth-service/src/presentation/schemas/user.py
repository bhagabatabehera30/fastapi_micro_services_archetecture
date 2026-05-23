from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    roles: list[str] = []

    @field_validator("roles", mode="before")
    @classmethod
    def serialize_roles(cls, v):
        if not v:
            return []
        if isinstance(v, list) and len(v) > 0 and hasattr(v[0], "name"):
            return [role.name for role in v]
        return v

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
