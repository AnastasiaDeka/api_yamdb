"""Модуль с функциями для валидации данных в модели пользователя."""
from django.core.exceptions import ValidationError

from users.constants import DISALLOWED_USERNAMES


def validate_username(value):
    """Проверяет, что имя пользователя не входит в список запрещённых."""
    if value.lower() in DISALLOWED_USERNAMES:
        raise ValidationError(
            f'Имя пользователя "{value}" запрещено для использования.'
        )
    return value
