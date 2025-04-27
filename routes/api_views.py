from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Route, Point
from .serializers import RouteSerializer, PointSerializer, RouteWithoutPointsSerializer

from drf_spectacular.utils import extend_schema

@extend_schema(
    operation_id="list_routes",
    responses={200: RouteWithoutPointsSerializer(many=True)},
    request=None,
    description="List all routes for the current user.")
class RouteListAPIView(APIView):
    def get(self, request):
        routes = Route.objects.filter(author=request.user)
        serializer = RouteWithoutPointsSerializer(routes, many=True)
        return Response(serializer.data)

@extend_schema(operation_id="retrieve_route")
class RouteDetailAPIView(APIView):
    def get(self, request, route_id):
        try:
            route = Route.objects.get(id=route_id, author=request.user)
        except Route.DoesNotExist:
            return Response({"error": "Route not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = RouteSerializer(route)
        return Response(serializer.data)

@extend_schema(operation_id="create_point")
class PointCreateAPIView(APIView):
    def post(self, request, route_id):
        try:
            route = Route.objects.get(id=route_id, author=request.user)
        except Route.DoesNotExist:
            return Response({"error": "Route not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PointSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not route.can_modify(request.user):
            return Response({"error": "You do not have permission to modify this route"}, status=status.HTTP_403_FORBIDDEN)

        serializer.save(route=route, order=route.get_points().count() + 1)
        return Response(serializer.data, status=status.HTTP_201_CREATED)