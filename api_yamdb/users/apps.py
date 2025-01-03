"""
Модуль конфигурации приложения пользователей.

Определяет настройки приложения `users` для проекта API YaMDb.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Конфигурация приложения пользователей."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
