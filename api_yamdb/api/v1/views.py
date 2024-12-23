"""API views для платформы Yamdb."""

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, mixins, filters
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action

from .filters import TitleFilter
from users.models import User
from reviews.models import Category, Genre, Title, Review
from .serializers import (
    TitleListSerializer, UserCreateSerializer, UserRecieveTokenSerializer, UserSerializer,
    CategorySerializer, GenreSerializer, TitleSerializer,
    ReviewSerializer, CommentSerializer, UserMeSerializer
)
from .permissions import (
    IsSuperUserOrAdmin, IsAdminOrReadOnly, IsAdminModeratorAuthorOrReadOnly
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
                {'username': existing_user.username,
                 'email': existing_user.email},
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

        if not user.confirmation_code == confirmation_code:
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

        send_email(user, email_type='activation')

        return Response(
            {'message': 'Ссылка для активации отправлена на email.'},
            status=status.HTTP_200_OK
        )


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления произведениями."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_class = TitleFilter
    search_fields = ('name', 'year', 'category__slug', 'genre__slug')
    queryset = Title.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleListSerializer
        return TitleSerializer


class CategoryGenreBaseViewSet(viewsets.GenericViewSet,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.ListModelMixin):
    """Базовый вьюсет для категорий и жанров."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def destroy(self, request, slug=None):
        instance = get_object_or_404(self.queryset.model, slug=slug)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAdminModeratorAuthorOrReadOnly,
    )
    pagination_class = PageNumberPagination

    def get_title(self):
        title_id = self.kwargs.get("title_id")
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def rating(self, request, *args, **kwargs):
        title = self.get_title()
        reviews = Review.objects.filter(title=title)

        if reviews.exists():
            # 0, если оAverage Rating is None
            average_rating = reviews.aggregate(Avg('score'))['score__avg'] or 0
        else:
            average_rating = title.rating

        title.rating = average_rating
        title.save()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)
        self.rating(self.request, title.id)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly, IsAdminModeratorAuthorOrReadOnly,
    )
    pagination_class = PageNumberPagination

    def get_review(self):
        review_id = self.kwargs.get("review_id")
        return get_object_or_404(Review, pk=review_id)

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
