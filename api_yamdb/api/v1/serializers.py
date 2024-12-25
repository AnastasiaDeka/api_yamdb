"""Модуль сериализаторов для API."""

import uuid

from django.shortcuts import get_object_or_404
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
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(required=False)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category')

    def create(self, validated_data):
        category_slug = self.context['request'].data.get('category')
        genre_slugs = self.context['request'].data.get('genre', [])

        # Get category instance
        category = get_object_or_404(Category, slug=category_slug)
        title = Title.objects.create(**validated_data, category=category)

        # Add genres
        if genre_slugs:
            genres = Genre.objects.filter(slug__in=genre_slugs)
            title.genre.set(genres)

        return title

    def update(self, instance, validated_data):
        category_slug = self.context['request'].data.get('category')
        genre_slugs = self.context['request'].data.get('genre', [])

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            instance.category = category

        if genre_slugs:
            genres = Genre.objects.filter(slug__in=genre_slugs)
            instance.genre.set(genres)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


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
