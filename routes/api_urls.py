from django.urls import path
from .api_views import *

urlpatterns = [
    path('', RouteListAPIView.as_view(), name='api_routes_list'),
    path('<int:route_id>/', RouteAPIView.as_view(), name='api_route'),
    path('<int:route_id>/points/', PointCreateAPIView.as_view(), name='api_point_create'),
    path('<int:route_id>/points/<int:point_id>/', PointAPIView.as_view(), name='api_point_detail'),
    path('<int:route_id>/points/<int:point_id>/delete/', PointDeleteAPIView.as_view(), name='api_point_delete'),
]