"""Классы разрешений для доступа к API."""

from rest_framework import permissions
from users.models import UserRole


class IsSuperUserOrAdmin(permissions.BasePermission):
    """Доступ для суперпользователей или администраторов."""

    def has_permission(self, request, view):
        """Проверяет, имеет ли пользователь доступ на основе его роли."""

        return (request.user
                and request.user.is_authenticated
                and (request.user.is_superuser
                     or request.user.role == UserRole.ADMIN
                     ))


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    """Доступ для администраторов, модераторов или авторов."""

    def has_object_permission(self, request, view, obj):
        """Проверяет доступ к объекту на основе роли пользователя."""
        if request.method in permissions.SAFE_METHODS:
            return True

        return (request.user and request.user.is_authenticated and (
            request.user.is_superuser
            or request.user.role in [UserRole.ADMIN, UserRole.MODERATOR]
            or obj.author == request.user
        ))


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Доступ только для администраторов на изменение.
    Остальные могут только читать.
    """

    def has_permission(self, request, view):
        """Проверяет доступ на основе метода запроса и роли пользователя."""
        return (
            request.method in permissions.SAFE_METHODS
            or IsSuperUserOrAdmin().has_permission(request, view)
        )
