from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Route, Point
from .serializers import RouteDetailsSerializer, PointSerializer, RouteSerializer

from drf_spectacular.utils import extend_schema

@extend_schema(
    responses={200: RouteSerializer(many=True)},
    description="List all routes for the current user.",
    tags=["Routes"])
class RouteListAPIView(APIView):
    def get(self, request):
        print(request.user)
        routes = Route.objects.filter(author=request.user)
        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data)

@extend_schema()
class RouteDetailAPIView(APIView):
    serializer_class = RouteDetailsSerializer

    def get(self, request, route_id):
        try:
            route = Route.objects.get(id=route_id, author=request.user)
        except Route.DoesNotExist:
            return Response({"error": "Route not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(route)
        return Response(serializer.data)

@extend_schema()
class PointCreateAPIView(APIView):
    serializer_class = PointSerializer

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