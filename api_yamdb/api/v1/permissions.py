"""Классы разрешений для доступа к API."""

from rest_framework import permissions


class IsSuperUserOrAdmin(permissions.BasePermission):
    """Доступ для суперпользователей или администраторов."""

    def has_permission(self, request, view):
        """Проверяет, имеет ли пользователь доступ на основе его роли."""
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    """Доступ для администраторов, модераторов или авторов."""

    def has_object_permission(self, request, view, obj):
        """Проверяет доступ к объекту на основе роли пользователя."""
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user
                and request.user.is_authenticated
                and (
                    request.user.is_admin
                    or request.user.is_moderator
                    or obj.author == request.user
                )
            )
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Только для админов на изменение, остальные — для чтения."""

    def has_permission(self, request, view):
        """Проверяет доступ на основе метода запроса и роли пользователя."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin()
