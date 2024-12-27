"""Модуль сериализаторов для API."""

import re
from datetime import datetime
from django.core.validators import RegexValidator

from rest_framework.exceptions import ValidationError

from rest_framework import serializers

from reviews.models import Category, Genre, Title, Comment, Review
from users.models import User
from users.validators import custom_username_validator

from django.contrib.auth.validators import UnicodeUsernameValidator

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


class BaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для произведений, категорий и жанров."""

    name = serializers.CharField(required=True)

    def validate_name(self, value):
        """Проверяет корректность имени пользователя."""
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
        """Проверяет корректность значения поля slug."""
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
        """Определяет модель и поля, которые будут сериализованы."""

        model = Category
        fields = ('name', 'slug')


class GenreSerializer(CategoryGenreBaseSerializer):
    """Сериализатор для жанров."""

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        model = Genre
        fields = ('name', 'slug')


class TitleListSerializer(BaseSerializer):
    """Сериализатор для списка произведений."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

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
        """Валидация года выпуска произведений."""
        current_year = datetime.now().year
        if not int(value) or value > current_year:
            raise ValidationError('Некорректный год')
        return value

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

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
        """Определяет модель и поля, которые будут сериализованы."""

        fields = ('id', 'author', 'text', 'score', 'pub_date')
        model = Review

    def validate_score(self, value):
        """Проверяет, находится ли оценка в пределах от 1 до 10."""
        if value < 1 or value > 10:
            raise serializers.ValidationError(
                'Score must be between 1 and 10.'
            )
        return value

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

        fields = ('id', 'author', 'pub_date', 'review', 'text')
        read_only_fields = ('review',)
        model = Comment
