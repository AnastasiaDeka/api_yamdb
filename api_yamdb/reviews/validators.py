"""Валидаторы для моделей."""

from django.utils import timezone
from django.core.exceptions import ValidationError


def year_validator(value):
    """Валидатор для года выпуска произведения."""
    if value > timezone.now().year:
        raise ValidationError('Год не может быть больше текущего')
