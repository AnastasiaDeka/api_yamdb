from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, SignupViewSet,
    TokenObtainViewSet,
    ResendConfirmationCodeViewSet, ActivateAccountViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'signup', SignupViewSet, basename='signup')
router.register(r'auth/token',
                TokenObtainViewSet, basename='token')
router.register(r'resend_confirmation_code',
                ResendConfirmationCodeViewSet,
                basename='resend_confirmation_code')
router.register(r'activate_account',
                ActivateAccountViewSet, basename='activate_account')

urlpatterns = [
    path('', include(router.urls)),
]
