from django.urls import path

from . import views

urlpatterns = [
    path('<int:image_id>', views.get_image, name='get_images'),
    path('', views.get_images, name='get_images'),
]