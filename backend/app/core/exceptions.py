"""Кастомные HTTP-исключения."""
from fastapi import HTTPException, status


class CredentialsError(HTTPException):
    def __init__(self, detail: str = "Не удалось проверить учётные данные"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotFoundError(HTTPException):
    def __init__(self, entity: str = "Объект"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity} не найден",
        )


class PermissionDeniedError(HTTPException):
    def __init__(self, detail: str = "Доступ запрещён"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class RoutingError(HTTPException):
    def __init__(self, detail: str = "Маршрут не может быть построен"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
