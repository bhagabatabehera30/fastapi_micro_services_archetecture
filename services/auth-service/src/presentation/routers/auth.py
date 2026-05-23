from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.dependencies import get_db_session
from src.infrastructure.repositories.user_repository import UserRepository
from src.application.use_cases.auth_usecase import AuthUseCase
from src.presentation.schemas.user import UserCreate, UserResponse, TokenResponse

router = APIRouter()

def get_auth_usecase(session: AsyncSession = Depends(get_db_session)) -> AuthUseCase:
    user_repo = UserRepository(session)
    return AuthUseCase(user_repo)

@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    auth_usecase: AuthUseCase = Depends(get_auth_usecase)
):
    return await auth_usecase.register_user(user_in)

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_usecase: AuthUseCase = Depends(get_auth_usecase)
):
    token = await auth_usecase.authenticate_user(form_data.username, form_data.password)
    return {"access_token": token, "token_type": "bearer"}
