from pydantic import BaseModel, EmailStr

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
    role: str

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
