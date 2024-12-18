from rest_framework import serializers
from django.contrib.auth.models import User

class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        """Создание пользователя."""
        user = User.objects.create_user(**validated_data)
        return user


class UserRecieveTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена по коду подтверждения."""
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=200)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения данных пользователя."""

    class Meta:
        model = User
        fields = ['username', 'email']


class UserActivateSerializer(serializers.Serializer):
    """Сериализатор для активации учетной записи через email."""
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=200)
