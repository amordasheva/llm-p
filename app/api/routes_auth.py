from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_usecase, get_current_user
from app.core.errors import ConflictError, UnauthorizedError
from app.db.models import User
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    auth_usecase: AuthUseCase = Depends(get_auth_usecase),
):
    try:
        return await auth_usecase.register(
            email=str(data.email),
            password=data.password,
        )
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=exc.message,
        ) from exc


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_usecase: AuthUseCase = Depends(get_auth_usecase),
):
    try:
        token = await auth_usecase.login(
            email=form_data.username,
            password=form_data.password,
        )
        return TokenResponse(access_token=token)
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.get("/me", response_model=UserPublic)
async def me(
    current_user: User = Depends(get_current_user),
):
    return current_user