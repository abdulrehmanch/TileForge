# app/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('<str:db>/', views.map_view, name='map_view'),
    path('tiles/<str:db>/<str:table>/<int:z>/<int:x>/<int:y>', views.serve_tile, name='serve_tile'),
]
