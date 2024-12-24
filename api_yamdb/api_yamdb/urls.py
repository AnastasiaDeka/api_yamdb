"""
Основной файл маршрутов для проекта.

Определяет маршруты для административной панели и приложения API.
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
    path('api/', include('api.urls')),
]
