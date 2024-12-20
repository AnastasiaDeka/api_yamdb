from rest_framework import permissions
from users.models import User


class IsSuperUserOrAdmin(permissions.BasePermission):
    """
    Доступ только для суперпользователей или администраторов.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == User.Role.ADMIN


class IsAdminModeratorAuthor(permissions.BasePermission):
    """
    Доступ для администраторов, модераторов или авторов.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.is_superuser
            or request.user.role in ['admin', 'moderator']
            or obj.author == request.user
        )


class ReadOnlyForAnon(permissions.BasePermission):
    """
    Доступ анонимным пользователям только на чтение.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or request.user.is_authenticated


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Доступ только для администраторов на изменение.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or IsSuperUserOrAdmin().has_permission(request, view)
        )
