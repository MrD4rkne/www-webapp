from django.urls import path

from . import views

urlpatterns = [
    path('', views.get_routes_view, name='get_routes_view'),
    path('create/<int:image_id>', views.create_route_view, name='create_route_view'),
    path('<int:route_id>', views.get_route_view, name='get_route_view'),
    path('<int:route_id>/delete', views.delete_route, name='delete_route'),
    path('<int:route_id>/points', views.create_point, name='create_point'),
    path('<int:route_id>/points/<int:point_id>/delete', views.delete_point, name='delete_point')
]