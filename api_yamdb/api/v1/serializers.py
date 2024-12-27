"""Модуль сериализаторов для API."""

import re
from datetime import datetime
from django.core.validators import RegexValidator
from rest_framework import serializers
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Genre, Title, Comment, Review
from users.models import User
from users.validators import custom_username_validator

MAX_USERNAME_LENGTH = 150
MAX_EMAIL_LENGTH = 254


class UserCreateSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    # Поле для имени пользователя с валидаторами
    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        validators=[
            # Валидатор от Django для проверки стандартного формата имени
            UnicodeUsernameValidator(),
            # Кастомный валидатор для запрета имени 'me'
            RegexValidator(
                regex=r'^(?!me$).*$', 
                message="Имя пользователя не может быть 'me'."
            )
        ],
        error_messages={
            "required": "Это поле обязательно для заполнения.",
            "max_length": "Длина имени пользователя не может превышать 150 символов.",
        }
    )

    # Поле для email с валидацией длины и формата
    email = serializers.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        error_messages={
            "required": "Это поле обязательно для заполнения.",
            "invalid": "Введите корректный адрес электронной почты.",
        }
    )

    def validate(self, data):
        """
        Кастомная валидация комбинации username и email.
        Проверяем, что пользователь с таким именем или email не существует.
        """
        username = data['username']  # Получаем username из данных
        email = data['email']  # Получаем email из данных

        # Проверка существующего пользователя с таким email
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': ["Пользователь с таким E-mail уже существует."]
            })

        # Проверка существующего пользователя с таким username
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({
                'username': ["Пользователь с таким именем уже существует."]
            })

        return data  # Возвращаем данные, если всё в порядке


class UserRecieveTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена по коду подтверждения."""

    # Поле для имени пользователя с добавленным валидатором для "me"
    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        validators=[
            UnicodeUsernameValidator(),
            RegexValidator(
                regex=r'^(?!me$).*$', 
                message='Имя пользователя не может быть "me".'
            )
        ],
        error_messages={
            "required": "Это поле обязательно для заполнения.",
            "max_length": (
                f"Длина имени пользователя не может превышать "
                f"{MAX_USERNAME_LENGTH} символов."
            ),
        }
    )

    # Поле для кода подтверждения
    confirmation_code = serializers.CharField(
        error_messages={
            "required": "Это поле обязательно для заполнения.",
        }
    )



class UserMeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с данными текущего пользователя."""

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')

    def update(self, instance, validated_data):
        """Метод для обновления данных текущего пользователя.
        Роль пользователя не изменяется.
        """
        # Удаляем поле 'role' из данных, если оно присутствует
        validated_data.pop('role', None)
        # Обновляем остальные поля
        return super().update(instance, validated_data)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )

    def to_representation(self, instance):
        """Преобразование ответа в соответствии с ТЗ."""
        representation = super().to_representation(instance)

        category = instance.category
        representation['category'] = {
            'name': category.name,
            'slug': category.slug
        } if category else None

        genres = instance.genre.all()
        representation['genre'] = [
            {'name': genre.name, 'slug': genre.slug} for genre in genres
        ]

        return representation


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для ревью."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        fields = ('id', 'author', 'text', 'score', 'pub_date')
        model = Review

    def create(self, validated_data):
        """Создаёт уникальный отзыв для пользователя и произведения."""
        user = validated_data['author']
        title = validated_data['title']

        if Review.objects.filter(author=user, title=title).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на этот title.'
            )

        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к ревью."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        fields = ('id', 'author', 'pub_date', 'text')
        model = Comment
