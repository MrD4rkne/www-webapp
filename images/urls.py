from django.urls import path

from . import views

urlpatterns = [
    path('images/<int:image_id>', views.get, name='get_images'),
]