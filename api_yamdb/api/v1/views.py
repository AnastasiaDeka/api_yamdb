"""API views для платформы Yamdb."""

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from rest_framework import (
    viewsets,
    permissions,
    status,
    mixins,
    filters,
)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action, api_view, permission_classes

from .filters import TitleFilter
from users.models import User
from reviews.models import Category, Genre, Title, Review
from .serializers import (
    TitleListSerializer, UserCreateSerializer,
    UserRecieveTokenSerializer,
    CategorySerializer, GenreSerializer, TitleSerializer,
    ReviewSerializer, CommentSerializer, UserMeSerializer,
)
from .permissions import (
    IsSuperUserOrAdmin, IsAdminOrReadOnly,
    IsAdminModeratorAuthorOrReadOnly
)
from .utils import send_email
from .viewsets import CategoryGenreBaseViewSet

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Управление пользователями."""

    queryset = User.objects.all()
    serializer_class = UserMeSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrAdmin)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['get', 'patch'], detail=False,
        url_path='me', permission_classes=(IsAuthenticated,)
    )
    def get_me_data(self, request):
        """Получение и обновление данных текущего пользователя."""
        user = request.user

        if request.method == 'PATCH':
            serializer = UserMeSerializer(user, data=request.data,
                                          partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_confirmation_view(request):
    """Создание пользователя или повторная отправка кода подтверждения."""
    serializer = UserCreateSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    email = serializer.validated_data['email']

    user, _ = User.objects.get_or_create(username=username, email=email)

    send_email(user)

    response_data = {'username': user.username, 'email': user.email}

    return Response(
        response_data,
        status=status.HTTP_200_OK
    )


class TokenObtainViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """Получение токена аутентификации."""

    serializer_class = UserRecieveTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """Выдает JWT токен по коду подтверждения."""
        serializer = UserRecieveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')

        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            return Response(
                {'confirmation_code': 'Код подтверждения невалиден'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = AccessToken.for_user(user, confirmation_code)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления произведениями."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_class = TitleFilter
    search_fields = ('name', 'year', 'category__slug', 'genre__slug')
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от действия."""
        if self.action == 'list':
            return TitleListSerializer
        return TitleSerializer


class CategoryViewSet(CategoryGenreBaseViewSet):
    """Вьюсет для управления категориями."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class GenreViewSet(CategoryGenreBaseViewSet):
    """Вьюсет для управления жанрами."""

    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления отзывами."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminModeratorAuthorOrReadOnly,
    )
    pagination_class = PageNumberPagination

    def get_title(self):
        """Получает объект произведения по переданному title_id."""
        title_id = self.kwargs.get("title_id")
        return get_object_or_404(Title, pk=title_id)

    def perform_create(self, serializer):
        """Создаёт отзыв, связывая его с автором и произведением."""
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления комментариями."""

    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAdminModeratorAuthorOrReadOnly,
    )
    pagination_class = PageNumberPagination

    def get_review(self):
        """Получает объект отзыва по переданному review_id."""
        review_id = self.kwargs.get("review_id")
        title_id = self.kwargs.get("title_id")
        return get_object_or_404(Review, pk=review_id, title_id=title_id)

    def get_queryset(self):
        """Возвращает список комментариев для конкретного отзыва."""
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        """Создаёт комментарий, связывая его с автором и отзывом."""
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
