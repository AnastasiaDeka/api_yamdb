"""
Модуль URL-конфигурации для API приложения Yamdb.

Этот модуль определяет маршруты для работы с пользователями, категориями,
жанрами, произведениями, отзывами и комментариями через Django Rest Framework.
Включает маршруты для регистрации, аутентификации и активации учётной записи.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserConfirmationViewSet,
    TokenObtainViewSet, ActivateAccountViewSet,
    CategoryViewSet, GenreViewSet, TitleViewSet,
    ReviewViewSet, CommentViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'signup', UserConfirmationViewSet, basename='signup')

router.register(r'auth/token',
                TokenObtainViewSet, basename='token')
router.register(r'resend_confirmation_code',
                UserConfirmationViewSet,
                basename='resend_confirmation_code')
router.register(r'activate_account',
                ActivateAccountViewSet, basename='activate_account')
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
    path('signup/',
         UserConfirmationViewSet.as_view({'post': 'create'}),
         name='signup'),
    path('token/',
         TokenObtainViewSet.as_view({'post': 'create'}),
         name='token'),
]

urlpatterns = [
    path('auth/', include(auth_urls)),
    path('', include(router.urls)),
]
