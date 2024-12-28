"""Вьюсеты для API."""

from rest_framework import viewsets, mixins, filters

from .permissions import IsAdminOrReadOnly


class CategoryGenreBaseViewSet(viewsets.GenericViewSet,
                               mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.ListModelMixin):
    """Базовый вьюсет для категорий и жанров."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
