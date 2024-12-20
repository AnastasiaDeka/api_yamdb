from rest_framework import serializers
from django.contrib.auth.models import User

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
