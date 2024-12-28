"""Модуль сериализаторов для API."""

import re
from datetime import datetime
from django.core.validators import RegexValidator
from rest_framework import serializers
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Genre, Title, Comment, Review
from users.models import User

MAX_USERNAME_LENGTH = 150
MAX_EMAIL_LENGTH = 254


class UserCreateSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        validators=[
            UnicodeUsernameValidator(),
            RegexValidator(
                regex=r'^(?!me$).*$',
                message='Имя пользователя не может быть "me".'
            ),
        ],
        error_messages={
            'required': 'Это поле обязательно для заполнения.',
            'max_length': (
                'Длина имени пользователя не может превышать 150 символов.'
            ),
        }
    )

    email = serializers.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        error_messages={
            'required': 'Это поле обязательно для заполнения.',
            'invalid': 'Введите корректный адрес электронной почты.',
        }
    )

    def validate(self, data):
        """Кастомная валидация комбинации username и email."""
        username = data.get('username')
        email = data.get('email')

        user_same_username = User.objects.filter(username=username).first()

        if user_same_username:
            if user_same_username.email != email:
                raise serializers.ValidationError({
                    'username': [
                        'Пользователь с таким именем уже существует,'
                        'но с другим email.'
                    ]
                })

        user_same_email = User.objects.filter(email=email).first()

        if user_same_email:
            if user_same_email.username != username:
                raise serializers.ValidationError({
                    'email': [
                        'Пользователь с таким E-mail уже существует,'
                        'но с другим именем.'
                    ]
                })

        return data


class UserRecieveTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена по коду подтверждения."""

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
            'required': 'Это поле обязательно для заполнения.',
            'max_length': (
                f'Длина имени пользователя не может превышать '
                f'{MAX_USERNAME_LENGTH} символов.'
            ),
        }
    )

    confirmation_code = serializers.CharField(
        error_messages={
            'required': 'Это поле обязательно для заполнения.',
        }
    )


class UserMeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с данными текущего пользователя."""

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio',
                  'role')

    def update(self, instance, validated_data):
        """Метод для обновления данных текущего пользователя."""
        validated_data.pop('role', None)
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


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к ревью."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        fields = ('id', 'author', 'pub_date', 'text')
        model = Comment
