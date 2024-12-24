"""
Модуль маршрутов для основной версии API платформы Yamdb.

Этот модуль включает маршруты для взаимодействия с API,
где обрабатываются запросы в рамках версии 1 ('v1') платформы.
"""
from django.urls import include, path


urlpatterns = [
    path('v1/', include('api.v1.urls'))
]
