from django.urls import path
from .views import create_background_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('create/', create_background_view, name='create_background')
]
