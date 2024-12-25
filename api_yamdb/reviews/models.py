"""
Модели для работы с произведениями, жанрами, категориями, отзывами.

Этот файл содержит определения моделей для категории, жанра, произведения,
произведения,отзыва и комментария,
а также базовую модель для категорий и жанров с уникальными
ограничениями на поля.
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, RegexValidator
from django.utils import timezone

from users.models import User

User = get_user_model()


class BaseModel(models.Model):
    """Базовая модель для моделей жанра и категории."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(
        unique=True,
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message=('Слаг может содержать только буквы,'
                         'цифры, подчеркивания и дефисы'),
            ),
        ]
    )

    class Meta:
        """Мета класс для базовой модели."""

        ordering = ('name', 'slug')
        abstract = True


class Category(BaseModel):
    """Модель категории."""

    def __str__(self):
        """Возвращает строковое представление модели."""
        return f'Категория: {self.name}'


class Genre(BaseModel):
    """Модель жанра."""

    def __str__(self):
        """Возвращает строковое представление модели."""
        return f'Жанр: {self.name}'


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(max_length=256)
    year = models.SmallIntegerField(
        validators=[MaxValueValidator(
            timezone.now().year,
            message='Год не может быть больше текущего'
        )]
    )
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(Genre, through='TitleGenre')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)

    class Meta:
        """Мета класс для модели Title."""

        ordering = ('name', 'year')

    def __str__(self):
        """Возвращает строковое представление произведения."""
        genres = ', '.join(self.genre.values_list('name', flat=True))
        return (f'Название: "{self.name}", '
                f'год выпуска: {self.year}, '
                f'категория: {self.category}, '
                f'жанр: {genres}')


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

    text = models.TextField()
    score = models.IntegerField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )

    class Meta:
        """Указывает уникальное ограничение на genre и title."""

        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_review_per_title')
        ]
        default_related_name = 'reviews'

    def __str__(self):
        """Возвращает текст отзыва."""
        return self.text


class Comment(models.Model):
    """Comment model."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    def __str__(self):
        """Возвращает автора и текст комментария."""
        return f'{self.author}, {self.review}'
