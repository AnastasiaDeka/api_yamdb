"""
Модели для работы с произведениями, жанрами, категориями, отзывами.

Этот файл содержит определения моделей для категории, жанра, произведения,
произведения,отзыва и комментария,
а также базовую модель для категорий и жанров с уникальными
ограничениями на поля.
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)

from users.models import User
from .validators import year_validator

MAX_NAME_LENGTH = 256
MAX_SLUG_LENGTH = 50
MIN_SCORE = 1
MAX_SCORE = 10

User = get_user_model()


class BaseModel(models.Model):
    """Базовая модель для моделей жанра и категории."""

    name = models.CharField(max_length=MAX_NAME_LENGTH)
    slug = models.SlugField(unique=True, max_length=MAX_SLUG_LENGTH)

    class Meta:
        """Мета класс для базовой модели."""

        ordering = ('name', 'slug')
        abstract = True


class Category(BaseModel):
    """Модель категории."""

    class Meta:
        """Мета класс для модели Category."""

        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        """Возвращает строковое представление модели."""
        return f'Категория: {self.name}'


class Genre(BaseModel):
    """Модель жанра."""

    class Meta:
        """Мета класс для модели Genre."""

        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        """Возвращает строковое представление модели."""
        return f'Жанр: {self.name}'


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(max_length=MAX_NAME_LENGTH)
    year = models.SmallIntegerField(validators=[year_validator])
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(Genre, through='TitleGenre')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)

    class Meta:
        """Мета класс для модели Title."""

        ordering = ('name', 'year')
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        """Возвращает строковое представление произведения."""
        return (f'Название: "{self.name}", год выпуска: {self.year}')


class TitleGenre(models.Model):
    """Модель TitleGenre для связи произведения и жанра."""

    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    title = models.ForeignKey(Title, on_delete=models.SET_NULL, null=True)

    class Meta:
        """Мета класс для модели TitleGenre."""

        constraints = [
            models.UniqueConstraint(
                fields=['genre', 'title'], name='unique_title_genre')
        ]


class Review(models.Model):
    """Review model."""

    text = models.TextField('Текст')
    score = models.IntegerField(
        validators=[
            MinValueValidator(
                MIN_SCORE,
                message=f'Оценка должна быть не меньше {MIN_SCORE}'
            ),
            MaxValueValidator(
                MAX_SCORE,
                message=f'Оценка должна быть не меньше {MAX_SCORE}'
            )
        ]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )

    class Meta:
        """Указывает уникальное ограничение на author и title."""

        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_review_per_title')
        ]
        default_related_name = 'reviews'

        ordering = ('pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        """Возвращает текст отзыва."""
        return f'Отзыв: {self.text}'


class Comment(models.Model):
    """Comment model."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        """Мета класс для модели Comment."""

        ordering = ('pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        """Возвращает автора и текст комментария."""
        return f'автор: {self.author}, отзыв: {self.review}'
