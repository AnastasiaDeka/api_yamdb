"""Модуль сериализаторов для API."""

import re
import uuid
from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from django.core.validators import RegexValidator

from reviews.models import Category, Genre, Title, Comment, Review
from users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        model = User
        fields = ['username', 'email']

    def create(self, validated_data):
        """Создание пользователя или обновление кода подтверждения."""
        user = User.objects.filter(username=validated_data['username'],
                                   email=validated_data['email']).first()

        if user:
            user.confirmation_code = str(uuid.uuid4())
            user.save()
            return user

        if User.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError({
                'email': ['Пользователь с таким E-mail уже существует.']
            })

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=None
        )
        user.set_unusable_password()
        return user

    def validate_username(self, value):
        """Проверка имени пользователя на недопустимые значения."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" недопустимо.')
        return value


class UserRecieveTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена по коду подтверждения."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=200)


class UserMeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с данными текущего пользователя."""

    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы.',
                code='invalid_username'
            )
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        error_messages={
            'max_length': 'E-mail не может быть длиннее 254 символов.'
        }
    )

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio')
        extra_kwargs = {
            'username': {'read_only': True},
            'email': {'read_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения данных пользователя."""

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class UserActivateSerializer(serializers.Serializer):
    """Сериализатор для активации учетной записи через email."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=200)


class BaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для произведений, категорий и жанров."""

    name = serializers.CharField(required=True)

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError('Имя не может быть пустым')
        if len(value) > 256:
            raise serializers.ValidationError(
                'Длина названия не должна превышать 256 символов'
            )
        return value


class CategoryGenreBaseSerializer(BaseSerializer):
    """Базовый сериализатор для категорий и жанров."""

    slug = serializers.SlugField(required=True)

    def validate_slug(self, value):
        if not re.match(r'^[-a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                'Слаг может содержать только латинские буквы, цифры, '
                'дефисы и знаки подчеркивания.')
        if self.Meta.model.objects.filter(slug=value).exists():
            raise serializers.ValidationError('Слаг уже существует')
        if len(value) > 50:
            raise serializers.ValidationError(
                'Длина слага не должна превышать 50 символов')
        return value


class CategorySerializer(CategoryGenreBaseSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(CategoryGenreBaseSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleListSerializer(BaseSerializer):
    """Сериализатор для списка произведений."""
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class TitleSerializer(BaseSerializer):
    """Сериализатор для произведений."""

    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    def validate_year(self, value):
        current_year = datetime.now().year
        if not int(value) or value > current_year:
            raise ValidationError('Некорректный год')
        return value

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для ревью."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'author', 'text', 'score', 'pub_date')
        #read_only_fields = ('author',)
        model = Review

    def validate_score(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Score must be between 1 and 10.")
        return value

    def create(self, validated_data):
        user = validated_data['author']
        title = validated_data['title']

        if Review.objects.filter(author=user, title=title).exists():
            raise serializers.ValidationError('Вы уже оставили отзыв на этот title.')
        
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к ревью."""
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'author', 'pub_date', 'review', 'text')
        read_only_fields = ('review',)
        model = Comment
