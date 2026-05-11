from app.db.models import ChatMessage
from app.repositories.chat_messages import ChatMessagesRepository
from app.services.openrouter_client import OpenRouterClient


class ChatUseCase:
    def __init__(
        self,
        messages_repository: ChatMessagesRepository,
        openrouter_client: OpenRouterClient,
    ):
        self._messages_repository = messages_repository
        self._openrouter_client = openrouter_client

    async def ask(
        self,
        user_id: int,
        prompt: str,
        system: str | None = None,
        max_history: int = 10,
        temperature: float = 0.7,
    ) -> str:
        messages: list[dict[str, str]] = []

        if system:
            messages.append(
                {
                    "role": "system",
                    "content": system,
                }
            )

        history = await self._messages_repository.get_last_messages(
            user_id=user_id,
            limit=max_history,
        )

        for item in history:
            messages.append(
                {
                    "role": item.role,
                    "content": item.content,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        await self._messages_repository.add_message(
            user_id=user_id,
            role="user",
            content=prompt,
        )

        answer = await self._openrouter_client.chat_completion(
            messages=messages,
            temperature=temperature,
        )

        await self._messages_repository.add_message(
            user_id=user_id,
            role="assistant",
            content=answer,
        )

        return answer

    async def get_history(self, user_id: int) -> list[ChatMessage]:
        return await self._messages_repository.get_all_messages(user_id)

    async def clear_history(self, user_id: int) -> None:
        await self._messages_repository.delete_all_messages(user_id)