"""Модель пользователя для проекта YaMDB."""
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from .validators import custom_username_validator
from django.db import models

from api.v1.constants import MAX_USERNAME_LENGTH, MAX_CONFIRMATION_CODE_LENGTH


class UserRole(models.TextChoices):
    """Роли пользователя."""

    ADMIN = 'admin', 'Admin'
    MODERATOR = 'moderator', 'Moderator'
    USER = 'user', 'User'


class UserManagerYaMDB(UserManager):
    """Менеджер для создания пользователей в проекте YaMDB."""

    def create_superuser(self,
                         username,
                         email=None,
                         password=None,
                         **extra_fields):
        """Создаёт суперпользователя с ролью администратора."""
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        return super().create_superuser(username,
                                        email,
                                        password,
                                        **extra_fields)


class User(AbstractUser):
    """Модель пользователя проекта YaMDB."""

    objects = UserManagerYaMDB()

    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[UnicodeUsernameValidator(), custom_username_validator],
        error_messages={
            'unique': "Пользователь с таким ником уже существует.",
        },
    )

    email = models.EmailField(
        unique=True,
        verbose_name='E-mail'
    )
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.USER,
        verbose_name='Роль'
    )
    bio = models.TextField(
        blank=True,
        default='',
        verbose_name='Биография'
    )
    confirmation_code = models.CharField(
        max_length=MAX_CONFIRMATION_CODE_LENGTH,
        blank=True,
        null=True,
        verbose_name='Код подтверждения'
    )

    class Meta:
        """Метаданные модели пользователя."""

        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        """Проверка на администратора."""
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Проверка на модератора."""
        return self.role == UserRole.MODERATOR

    @classmethod
    def roles(cls):
        """Возвращает список всех ролей пользователя."""
        return [role[0] for role in UserRole.choices]

    def __str__(self):
        """Строковое представление пользователя."""
        return self.username
