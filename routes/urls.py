from django.urls import path

from . import views

urlpatterns = [
    path('', views.post_route, name='post_route_view'),
    path('g', views.get_routes, name='get_routes_view'),
]