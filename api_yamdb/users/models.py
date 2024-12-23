"""Модель пользователя для проекта YaMDB."""
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
import uuid
from datetime import timedelta


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
        extra_fields.setdefault('role', UserRole.ADMIN)
        return super().create_superuser(username,
                                        email,
                                        password,
                                        **extra_fields)


class User(AbstractUser):
    """Модель пользователя проекта YaMDB."""

    objects = UserManagerYaMDB()

    email = models.EmailField(
        unique=True,
        max_length=254,
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
        null=True,
        verbose_name='Биография'
    )
    confirmation_code = models.CharField(
        max_length=36,
        blank=True,
        null=True,
        verbose_name='Код подтверждения'
    )
    confirmation_code_expiry = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Срок действия кода подтверждения'
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

    def is_confirmation_code_valid(self):
        """Проверяет, истек ли срок действия кода подтверждения."""
        return (
            self.confirmation_code_expiry and
            (self.confirmation_code_expiry > timezone.now())
        )

    def generate_new_confirmation_code(self):
        """Генерирует новый код подтверждения."""
        self.confirmation_code = str(uuid.uuid4())
        self.confirmation_code_expiry = timezone.now() + timedelta(minutes=15)
        self.save()
