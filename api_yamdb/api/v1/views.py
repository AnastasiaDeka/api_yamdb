from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.contrib.auth.tokens import default_token_generator
from rest_framework import viewsets, permissions, status, mixins, filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from datetime import timedelta

from users.models import User
from reviews.models import Category, Genre, Title, Review
from .serializers import (
    UserCreateSerializer, UserRecieveTokenSerializer, UserSerializer,
    CategorySerializer, GenreSerializer, TitleSerializer,
    ReviewSerializer, CommentSerializer, UserMeSerializer
)
from .permissions import (
    IsSuperUserOrAdmin, IsAdminOrReadOnly, IsAdminModeratorAuthor,
    ReadOnlyForAnon
)
from .utils import send_email


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Управление пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrAdmin)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def update(self, request, *args, **kwargs):
        """Запрещает PUT метод."""
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    @action(
        methods=['get', 'patch'], detail=False,
        url_path='me', permission_classes=(IsAuthenticated,)
    )
    def get_me_data(self, request):
        """Получение и обновление данных текущего пользователя."""
        user = request.user
        if request.method == 'PATCH':
            if user.is_superuser:
                serializer = UserSerializer(
                    user, data=request.data, partial=True
                )
            else:
                serializer = UserMeSerializer(
                    user, data=request.data, partial=True
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)

        serializer = self.get_serializer(user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)


class UserConfirmationViewSet(viewsets.GenericViewSet,
                              mixins.CreateModelMixin):
    """Создание пользователя и повторная отправка кода подтверждения."""
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        """Создает пользователя или отправляет код повторно."""
        required_fields = ['username', 'email']
        missing_fields = {
            field: [f"Поле '{field}' обязательно для заполнения."]
            for field in required_fields if not request.data.get(field)
        }
        if missing_fields:
            return Response(missing_fields, status=status.HTTP_400_BAD_REQUEST)

        username = request.data.get('username')
        email = request.data.get('email')

        existing_user = User.objects.filter(username=username,
                                            email=email).first()
        if existing_user:
            send_email(existing_user, email_type='confirmation')
            return Response(
                {'username': existing_user.username, 'email': existing_user.email},
                status=status.HTTP_200_OK
            )

        response = super().create(request, *args, **kwargs)
        new_user = User.objects.get(username=username, email=email)
        send_email(new_user, email_type='confirmation')
        response.status_code = status.HTTP_200_OK
        return response


class TokenObtainViewSet(viewsets.GenericViewSet,
                         mixins.CreateModelMixin):
    """Получение токена аутентификации."""
    serializer_class = UserRecieveTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """Выдает JWT токен по коду подтверждения."""
        serializer = UserRecieveTokenSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')

        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user,
                                                   confirmation_code):
            message = {'confirmation_code': 'Код подтверждения невалиден'}
            return Response(message,
                            status=status.HTTP_400_BAD_REQUEST)

        token = AccessToken.for_user(user)
        message = {'token': str(token)}
        return Response(message,
                        status=status.HTTP_200_OK)


class ActivateAccountViewSet(viewsets.GenericViewSet):
    """Активация аккаунта через email."""
    serializer_class = UserRecieveTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """Отправка ссылки для активации аккаунта на email."""
        serializer = UserRecieveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)

        send_confirmation_email(user, email_type='activation')

        return Response(
            {'message': 'Ссылка для активации отправлена на email.'},
            status=status.HTTP_200_OK
        )


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления произведениями."""
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'category', 'genre', 'year')
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class CategoryGenreBaseViewSet(viewsets.GenericViewSet,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.ListModelMixin):
    """Базовый вьюсет для категорий и жанров."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(CategoryGenreBaseViewSet):
    """Вьюсет для управления категориями."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class GenreViewSet(CategoryGenreBaseViewSet):
    """Вьюсет для управления жанрами."""

    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAdminOrReadOnly, ReadOnlyForAnon,
    )

    def get_title(self):
        title_id = self.kwargs.get("title_id")
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()
    
    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().annotate(avg_score=Avg('score'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (
        IsAdminModeratorAuthor, ReadOnlyForAnon,
    )

    def get_review(self):
        review_id = self.kwargs.get("review_id")
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)