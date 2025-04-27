from django.urls import path
from .api_views import RouteListAPIView, RouteDetailAPIView, PointCreateAPIView

urlpatterns = [
    path('', RouteListAPIView.as_view(), name='api_routes_list'),
    path('<int:route_id>/', RouteDetailAPIView.as_view(), name='api_route_detail'),
    path('<int:route_id>/points/', PointCreateAPIView.as_view(), name='api_point_create'),
]