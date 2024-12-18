from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Кастомная модель пользователя с ролями и биографией.
    """
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    bio = models.TextField(blank=True, null=True)

    @property
    def is_admin(self):
        """
        Проверка на администратора.
        """
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        """
        Проверка на модератора.
        """
        return self.role == 'moderator'

    def __str__(self):
        """
        Строковое представление пользователя.
        """
        return self.username
