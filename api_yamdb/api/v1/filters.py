"""Фильтрация произведений по категории, жанру, году и названию."""
import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """Фильтр произведений по категории, жанру, году и названию."""

    category = django_filters.CharFilter(
        field_name='category__slug', lookup_expr='iexact')
    genre = django_filters.CharFilter(
        field_name='genre__slug', lookup_expr='iexact')
    name = django_filters.CharFilter(
        field_name='name', lookup_expr='icontains')

    class Meta:
        """Модель и поля для фильтрации."""

        model = Title
        fields = ('category', 'genre', 'year', 'name')
