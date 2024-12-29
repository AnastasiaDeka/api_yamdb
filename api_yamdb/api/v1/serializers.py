"""Модуль сериализаторов для API."""
from rest_framework import serializers
from django.contrib.auth.validators import UnicodeUsernameValidator

from reviews.models import Category, Genre, Title, Comment, Review
from users.models import User

from users.constants import MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH
from users.validators import validate_username


class UserCreateSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        validators=[
            UnicodeUsernameValidator(),
            validate_username,
        ],
        error_messages={
            'required': 'Это поле обязательно для заполнения.',
            'max_length': (
                f'Длина имени пользователя не может превышать '
                f'{MAX_USERNAME_LENGTH} символов.'
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
        errors = {}

        username = data.get('username')
        email = data.get('email')

        user_same_username = User.objects.filter(username=username).first()
        if user_same_username:
            if user_same_username.email != email:
                errors['username'] = [
                    'Пользователь с таким именем уже существует,'
                    'но с другим email.'
                ]

        user_same_email = User.objects.filter(email=email).first()
        if user_same_email:
            if user_same_email.username != username:
                errors['email'] = [
                    'Пользователь с таким E-mail уже существует, '
                    'но с другим именем.'
                ]

        if errors:
            raise serializers.ValidationError(errors)

        return data


class UserRecieveTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена по коду подтверждения."""

    username = serializers.CharField(
        max_length=MAX_USERNAME_LENGTH,
        validators=[
            UnicodeUsernameValidator(),
            validate_username,
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


class TitleListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'category', 'genre')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=True
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all(),
        required=True
    )

    def validate_genre(self, value):
        """Проверка, что список жанров не пуст."""
        if not value:
            raise serializers.ValidationError(
                'Список жанров не может быть пустым.'
            )
        return value

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
        )

    def to_representation(self, instance):
        """Преобразование ответа в соответствии с ТЗ."""
        return TitleListSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для ревью."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        fields = ('id', 'author', 'text', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        """Проверяем уникальность отзыва для пользователя и произведения."""
        request = self.context.get('request')
        if request and request.method == 'POST':
            user = self.context['request'].user
            title = self.context['view'].kwargs.get('title_id')

            if Review.objects.filter(author=user, title_id=title).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к ревью."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        """Определяет модель и поля, которые будут сериализованы."""

        fields = ('id', 'author', 'pub_date', 'text')
        model = Comment
