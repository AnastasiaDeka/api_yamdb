"""Модель пользователя для проекта YaMDB."""
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from users.constants import (
    MAX_USERNAME_LENGTH, MAX_ROLE_LENGTH)
from .validators import custom_username_validator


class UserRole(models.TextChoices):
    """Роли пользователя."""

    ADMIN = 'admin', 'Admin'
    MODERATOR = 'moderator', 'Moderator'
    USER = 'user', 'User'


class User(AbstractUser):
    """Модель пользователя проекта YaMDB."""

    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[UnicodeUsernameValidator(),
                    custom_username_validator],
        error_messages={
            'unique': 'Пользователь с таким ником уже существует.',
        },
        verbose_name='Имя пользователя'
    )

    email = models.EmailField(
        unique=True,
        verbose_name='E-mail'
    )

    role = models.CharField(
        max_length=MAX_ROLE_LENGTH,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Роль'
    )

    bio = models.TextField(
        blank=True,
        default='',
        verbose_name='Биография'
    )

    class Meta:
        """Метаданные модели пользователя."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    @property
    def is_admin(self):
        """Проверка на администратора."""
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Проверка на модератора."""
        return self.role == UserRole.MODERATOR

    def __str__(self):
        """Строковое представление пользователя."""
        return f"{self.username} ({self.role})"
