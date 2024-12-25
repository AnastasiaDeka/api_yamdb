"""Модуль сериализаторов для API."""
from rest_framework import serializers
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.shortcuts import get_object_or_404
from .constants import MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH

from reviews.models import Category, Genre, Title, Comment, Review
from users.models import User
from users.validators import custom_username_validator


class UserCreateSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        validators=[UnicodeUsernameValidator()],
        error_messages={
            "required": "Это поле обязательно для заполнения.",
            "max_length": (
                "Длина имени пользователя не может превышать 150 символов."
            ),
        }
    )

    email = serializers.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        error_messages={
            "required": "Это поле обязательно для заполнения.",
            "invalid": "Введите корректный адрес электронной почты.",
        }
    )

    def validate_username(self, value):
        """Проверка валидности имени пользователя."""
        custom_username_validator(value)
        return value

    def validate(self, data):
        """Кастомная валидация комбинации username и email."""
        username = data.get('username')
        email = data.get('email')

        user_by_email = User.objects.filter(email=email).first()
        user_by_username = User.objects.filter(username=username).first()

        if (user_by_email and user_by_username
                and user_by_email != user_by_username):
            error_msg = {}

            if user_by_email:
                error_msg['email'] = [
                    'Пользователь с таким E-mail уже существует.'
                ]
            if user_by_username:
                error_msg['username'] = [
                    'Пользователь с таким именем уже существует.'
                ]

            raise serializers.ValidationError(error_msg)

        if user_by_email:
            raise serializers.ValidationError({
                'email': ['Пользователь с таким E-mail уже существует.']
            })

        if user_by_username:
            raise serializers.ValidationError({
                'username': ['Пользователь с таким именем уже существует.']
            })

        return data

    def create(self, validated_data):
        """Создание пользователя или обновление кода подтверждения."""
        user = User.objects.filter(
            username=validated_data['username'],
            email=validated_data['email']
        ).first()

        if user:
            user.generate_new_confirmation_code()
            return user

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_unusable_password()
        return user


class UserRecieveTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена по коду подтверждения."""

    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        validators=[UnicodeUsernameValidator()],
        error_messages={
            "required": "Это поле обязательно для заполнения.",
            "max_length": (
                f"Длина имени пользователя не может превышать "
                f"{MAX_USERNAME_LENGTH} символов."
            ),
        }
    )

    confirmation_code = serializers.CharField(
        error_messages={
            "required": "Это поле обязательно для заполнения.",
        }
    )

    def validate_username(self, value):
        """Кастомная валидация имени пользователя."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" недопустимо.'
            )
        return value


class UserMeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с данными текущего пользователя."""

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения данных пользователя."""

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


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
