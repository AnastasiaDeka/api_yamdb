import re
from datetime import datetime

from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Genre, Title, Comment, Review

from users.models import User

from reviews.models import Comment, Review, Category, Genre, Title

class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def validate_username(self, value):
        """Проверка запрета на 'me'."""
        if value.lower() == 'me':
            raise ValidationError("Username 'me' использовать нельзя.")
        return value

    def create(self, validated_data):
        """Создание пользователя."""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user


class UserRecieveTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена по коду подтверждения."""
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=200)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения данных пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role')


class UserActivateSerializer(serializers.Serializer):
    """Сериализатор для активации учетной записи через email."""
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=200)


class BaseSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для произведений, категорий и жанров."""
    name = serializers.CharField(required=True)

    def validate_name(self, value):
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
        fields = '__all__'


class GenreSerializer(CategoryGenreBaseSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = '__all__'


class TitleSerializer(BaseSerializer):
    """Сериализатор для произведений."""
    genre = serializers.SlugRelatedField(
        many=True, queryset=Genre.objects.all(), slug_field='slug', required=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug', required=True
    )

    def validate_year(self, value):
        current_year = datetime.now().year
        if value > current_year:
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

    class Meta:
        fields = ('id', 'author', 'text', 'score', 'pub_date')
        read_only_fields = ('author',)
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к ревью."""

    class Meta:
        fields = ('id', 'author', 'created', 'review', 'text')
        read_only_fields = ('author', 'review',)
        model = Comment
