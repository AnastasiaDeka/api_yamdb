from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.contrib.auth.tokens import default_token_generator

from rest_framework import viewsets, permissions, status, mixins, filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action

from reviews.models import Category, Genre, Title, Review
from .serializers import (
    UserCreateSerializer, UserRecieveTokenSerializer, UserSerializer,
    CategorySerializer, GenreSerializer, TitleSerializer, 
    ReviewSerializer, CommentSerializer
)
from .permissions import IsSuperUserOrAdmin, IsAdminOrReadOnly, IsAdminModeratorAuthor, ReadOnlyForAnon
from .utils import send_email

from .permissions import IsSuperUserOrAdmin, IsAdminOrReadOnly
User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления пользователями."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"
    filter_backends = [SearchFilter]
    search_fields = ["username"]

    action_permissions = {
        'list': [permissions.IsAdminUser],
        'retrieve': [permissions.IsAuthenticated],
        'create': [permissions.IsAuthenticated],
        'get_me_data': [permissions.IsAuthenticated],
        'update': [permissions.IsAdminUser],
        'partial_update': [permissions.IsAdminUser],
        'destroy': [permissions.IsAdminUser],
    }

    def get_permissions(self):
        """Устанавливает разрешения для разных действий."""
        permission_classes = self.action_permissions.get(self.action, [permissions.IsAdminUser])
        return [permission() for permission in permission_classes]

    @action(
        detail=False,
        methods=['get', 'patch', 'delete'],
        url_path='me',
        url_name='me',
        permission_classes=[permissions.IsAuthenticated]
    )
    def get_me_data(self, request):
        """Позволяет пользователю получить и обновить информацию о себе."""
        user = request.user

        if request.method == 'DELETE':
            return Response(
            {"detail": "DELETE method is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

        if request.method == 'PATCH':
            if request.user != user:
                return Response(
                    {"detail": "You can only update your own data."},
                    status=status.HTTP_403_FORBIDDEN
                )
            return self.update_user_data(user, request.data)

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update_user_data(self, user, data):
        """Обновление данных пользователя."""
        serializer = self.get_serializer(
            user, data=data, partial=True, context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)

        return Response(serializer.data, status=status.HTTP_200_OK)



class SignupViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """Вьюсет для регистрации пользователей."""

    serializer_class = UserCreateSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """Создает объект пользователя и отправляет код подтверждения."""
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        user, created = User.objects.get_or_create(username=username, email=email)
        
        if not created:
            if not user.confirmation_code:
                user.confirmation_code = str(uuid.uuid4())
                user.save()
            send_email(user, email_type='confirmation')
            return Response(
                {"message": "Код подтверждения отправлен повторно."},
                status=status.HTTP_200_OK
            )

        send_email(user, email_type='confirmation')

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