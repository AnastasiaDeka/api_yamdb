"""
Модуль URL-конфигурации для API приложения Yamdb.

Этот модуль определяет маршруты для работы с пользователями, категориями,
жанрами, произведениями, отзывами и комментариями через Django Rest Framework.
Включает маршруты для регистрации, аутентификации и активации учётной записи.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    TokenObtainViewSet,
    CategoryViewSet, GenreViewSet, TitleViewSet,
    ReviewViewSet, CommentViewSet, user_confirmation_view,
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register(r'auth/token',
                TokenObtainViewSet, basename='token')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

auth_urls = [
    path('signup/', user_confirmation_view, name='signup'),
    path('token/', TokenObtainViewSet.as_view({'post': 'create'}),
         name='token'),
]

urlpatterns = [
    path('auth/', include(auth_urls)),
    path('', include(router.urls)),
]
