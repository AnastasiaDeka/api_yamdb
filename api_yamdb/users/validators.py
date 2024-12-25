"""Модуль с функциями для валидации данных в модели пользователя."""
import re
from django.core.exceptions import ValidationError


def custom_username_validator(value):
    """Проверка недопустимых символов и зарезервированных ников."""
    if value.lower() == "me":
        raise ValidationError(
            "Ник 'me' зарезервирован и не может быть использован."
        )

    disallowed_symbols = re.compile(r'[^a-zA-Z0-9_]')
    if disallowed_symbols.search(value):
        raise ValidationError(
            f"Ник '{value}' содержит недопустимые символы. "
            "Разрешены только латинские буквы, цифры и символ '_'."
        )
