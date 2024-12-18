from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Кастомная модель пользователя с ролями и биографией.
    """

    class Role(models.TextChoices):
        USER = 'user', 'User'
        MODERATOR = 'moderator', 'Moderator'
        ADMIN = 'admin', 'Admin'

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    bio = models.TextField(blank=True, null=True)

    @property
    def is_admin(self):
        """
        Проверка на администратора.
        """
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """
        Проверка на модератора.
        """
        return self.role == self.Role.MODERATOR

    def __str__(self):
        """
        Строковое представление пользователя.
        """
        return self.username
