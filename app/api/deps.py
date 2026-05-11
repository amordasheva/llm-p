from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import AsyncSessionLocal
from app.repositories.chat_messages import ChatMessagesRepository
from app.repositories.users import UsersRepository
from app.services.openrouter_client import OpenRouterClient
from app.usecases.auth import AuthUseCase
from app.usecases.chat import ChatUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_users_repository(
    session: AsyncSession = Depends(get_session),
) -> UsersRepository:
    return UsersRepository(session)


def get_messages_repository(
    session: AsyncSession = Depends(get_session),
) -> ChatMessagesRepository:
    return ChatMessagesRepository(session)


def get_openrouter_client() -> OpenRouterClient:
    return OpenRouterClient()


def get_auth_usecase(
    users_repository: UsersRepository = Depends(get_users_repository),
) -> AuthUseCase:
    return AuthUseCase(users_repository)


def get_chat_usecase(
    messages_repository: ChatMessagesRepository = Depends(get_messages_repository),
    openrouter_client: OpenRouterClient = Depends(get_openrouter_client),
) -> ChatUseCase:
    return ChatUseCase(
        messages_repository=messages_repository,
        openrouter_client=openrouter_client,
    )


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise UnauthorizedError("Invalid token payload")

        return int(user_id)

    except (UnauthorizedError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    auth_usecase: AuthUseCase = Depends(get_auth_usecase),
):
    try:
        return await auth_usecase.get_profile(user_id)
    except NotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        ) from exc