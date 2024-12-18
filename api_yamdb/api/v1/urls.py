from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, SignupViewSet,
    TokenObtainViewSet,
    ResendConfirmationCodeViewSet, ActivateAccountViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'resend_confirmation_code', ResendConfirmationCodeViewSet, basename='resend_confirmation_code')
router.register(r'activate_account', ActivateAccountViewSet, basename='activate_account')

auth_urls = [
    path('signup/', SignupViewSet.as_view({'post': 'create'}), name='signup'),
    path('token/', TokenObtainViewSet.as_view({'post': 'create'}), name='token'),
]

urlpatterns = [
    path('auth/', include(auth_urls)),
    path('', include(router.urls)),
]
