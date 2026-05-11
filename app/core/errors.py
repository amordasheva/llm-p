class AppError(Exception):
    """Базовая ошибка приложения."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ConflictError(AppError):
    """Конфликт данных, например email уже занят."""


class UnauthorizedError(AppError):
    """Ошибка авторизации."""


class ForbiddenError(AppError):
    """Недостаточно прав."""


class NotFoundError(AppError):
    """Объект не найден."""


class ExternalServiceError(AppError):
    """Ошибка внешнего сервиса, например OpenRouter."""