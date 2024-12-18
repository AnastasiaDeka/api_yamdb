from rest_framework import permissions
from users.models import User

class IsSuperUserOrAdmin(permissions.BasePermission):
    """
    Доступ только для суперпользователей или администраторов.
    """

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.role == User.Role.ADMIN


class IsAdminModeratorAuthor(permissions.BasePermission):
    """
    Доступ для администраторов, модераторов или авторов.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.is_superuser
            or request.user.role in [User.Role.ADMIN, User.Role.MODERATOR]
            or obj.author == request.user
        )


class ReadOnlyForAnon(permissions.BasePermission):
    """
    Доступ анонимным пользователям только на чтение.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or request.user.is_authenticated
