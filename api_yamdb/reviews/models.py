from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class BaseModel(models.Model):
    """Базовая модель для моделей жанра и категории"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        """Мета класс для базовой модели"""
        ordering = ['-name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'slug'], name='unique_name_slug')
        ]


class Category(BaseModel):
    """Модель категории"""


class Genre(BaseModel):
    """Модель жанра"""


class Title(models.Model):
    """Модель произведения"""
    name = models.CharField(max_length=200)
    year = models.IntegerField()
    rating = models.IntegerField()
    description = models.TextField()
    genre = models.ManyToManyField(Genre, through='TitleGenre')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

    class Meta:
        """Мета класс для модели Title"""
        ordering = ['-id']


class TitleGenre(models.Model):
    """Модель TitleGenre для связи произведения и жанра"""
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    title = models.ForeignKey(Title, on_delete=models.SET_NULL, null=True)

    class Meta:
        """Мета класс для модели TitleGenre"""
        constraints = [
            models.UniqueConstraint(
                fields=['genre', 'title'], name='unique_title_genre')
        ]


class Review(models.Model):
    """Review model"""
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
        default_related_name = 'reviews'

    def __str__(self):
        return self.text



class Comment(models.Model):
    """Comment model"""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    def __str__(self):
        return f'{self.author}, {self.review}'
