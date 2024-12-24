"""
Модуль конфигурации приложения для API платформы Yamdb.

Этот модуль содержит класс конфигурации для приложения API,
которое управляет основными маршрутаами и логикой взаимодействия
с пользователями, произведениями, отзывами и комментариями.
"""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Конфигурация приложения для API платформы Yamdb."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
