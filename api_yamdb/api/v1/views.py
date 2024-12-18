from rest_framework import viewsets, permissions, status, mixins
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import filters
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import (
    UserCreateSerializer, UserRecieveTokenSerializer, UserSerializer
)
from .permissions import IsSuperUserOrAdmin

User = get_user_model()


def send_confirmation_email(user, email_type='confirmation'):
    """Отправка email с кодом подтверждения или активации."""
    # Ваша логика отправки email
    pass


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления пользователями."""

    serializer_class = UserSerializer
    permission_classes = (IsSuperUserOrAdmin,)
    queryset = User.objects.all()
    lookup_field = "username"
    filter_backends = [filters.SearchFilter]
    search_fields = ["username"]


class SignupViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """Вьюсет для регистрации пользователей."""

    serializer_class = UserCreateSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """Создает объект пользователя и отправляет код подтверждения."""
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if User.objects.filter(username=serializer.validated_data['username']).exists():
            raise ValidationError("Пользователь с таким именем уже существует.")

        user, _ = User.objects.get_or_create(**serializer.validated_data)

        send_confirmation_email(user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenObtainViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """Вьюсет для получения токена аутентификации."""

    serializer_class = UserRecieveTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """Предоставляет пользователю JWT токен по коду подтверждения."""
        serializer = UserRecieveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')

        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            message = {'confirmation_code': 'Код подтверждения невалиден'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

        message = {'token': str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)


class ResendConfirmationCodeViewSet(viewsets.GenericViewSet,
                                    mixins.CreateModelMixin):
    """Вьюсет для повторной отправки кода подтверждения на email."""

    serializer_class = UserRecieveTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """Отправка повторного кода подтверждения."""
        serializer = UserRecieveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')

        user = get_object_or_404(User, username=username)

        send_confirmation_email(user)

        return Response(
            {'message': 'Код подтверждения отправлен на email.'},
            status=status.HTTP_201_OK
        )


class ActivateAccountViewSet(viewsets.GenericViewSet):
    """Вьюсет для активации учетной записи через email."""

    serializer_class = UserRecieveTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """Отправка ссылки для активации учетной записи на email."""
        serializer = UserRecieveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)

        send_confirmation_email(user, email_type='activation')

        return Response(
            {'message': 'Ссылка для активации учетной записи отправлена на email.'},
            status=status.HTTP_200_OK
        )
