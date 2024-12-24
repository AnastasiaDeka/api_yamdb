"""Конфигурация приложения для работы с отзывами и комментариями."""
from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """
    Конфигурация приложения отзывов.

    Этот класс отвечает за настройки приложения для работы с отзывами,
    комментариями и их связями в системе.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'
