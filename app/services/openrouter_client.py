from typing import Any

import httpx

from app.core.config import settings
from app.core.errors import ExternalServiceError


class OpenRouterClient:
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
    ) -> str:
        if not settings.openrouter_api_key:
            raise ExternalServiceError("OpenRouter API key is not configured")

        url = f"{settings.openrouter_base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "model": settings.openrouter_model,
            "messages": messages,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise ExternalServiceError("OpenRouter request failed") from exc

        if response.status_code >= 400:
            raise ExternalServiceError(
                f"OpenRouter error: {response.status_code} {response.text}"
            )

        data = response.json()

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ExternalServiceError("Invalid OpenRouter response") from exc