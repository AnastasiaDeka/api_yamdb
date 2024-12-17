from django.db import models


class Category(models.Model):
    """Category model"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Genre model"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Title model"""
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
        ordering = ['-id']


class TitleGenre(models.Model):
    """TitleGenre model"""
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    title = models.ForeignKey(Title, on_delete=models.SET_NULL, null=True)

    class Meta:
        """Meta class for TitleGenre model"""
        constraints = [
            models.UniqueConstraint(
                fields=['genre', 'title'], name='unique_title_genre')
        ]
