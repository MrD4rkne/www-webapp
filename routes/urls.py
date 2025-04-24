from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_routes_view, name='get_routes_view'),
    path('create/{image_id}', views.create_route, name='create_route')
]