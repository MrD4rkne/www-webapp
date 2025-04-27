from django.urls import path
from .api_views import *

urlpatterns = [
    path('', ImageListAPIView.as_view(), name='api_images_list'),
    path('<int:image_id>/', ImageGetAPIView.as_view(), name='api_image_detail'),
]