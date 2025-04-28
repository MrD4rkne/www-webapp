from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from images import models as images_models
from .serializers import *

from drf_spectacular.utils import extend_schema, OpenApiResponse

class RouteListAPIView(APIView):
    @extend_schema(
        responses={200: RouteSerializer(many=True)},
        description="List all routes for the current user.",
        tags=["Routes"])
    def get(self, request):
        routes = Route.objects.filter(author=request.user)
        serializer = RouteSerializer(routes, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=RouteCreateSerializer,
        responses={
            201: RouteSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Image not found")
        },
        description="Create a new route.",
        tags=["Routes"]
    )
    def post(self, request):
        serializer = RouteCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            image = images_models.Image.objects.get(id=request.data['image'])
        except images_models.Image.DoesNotExist:
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        if not image.can_access(request.user):
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RouteAPIView(APIView):
    serializer_class = RouteDetailsSerializer

    @extend_schema(
        responses={200: RouteDetailsSerializer,
                   404: OpenApiResponse(description="Route not found")},
        description="Get details of a specific route.",
        tags=["Routes"]
    )
    def get(self, request, route_id):
        try:
            route = Route.objects.get(id=route_id)
        except Route.DoesNotExist:
            return Response({"error": "Route not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(route)
        return Response(serializer.data)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Route deleted"),
            403: OpenApiResponse(description="You do not have permission to modify this route"),
            404: OpenApiResponse(description="Route not found")
        },
        description="Delete a route.",
        tags=["Routes"]
    )
    def delete(self, request, route_id):
        try:
            route = Route.objects.get(id=route_id)
        except Route.DoesNotExist:
            return Response({"error": "Route not found"}, status=status.HTTP_404_NOT_FOUND)

        if not route.can_modify(request.user):
            return Response({"error": "You do not have permission to modify this route"},
                            status=status.HTTP_403_FORBIDDEN)

        route.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(
    request=PointSerializer,
    responses={201: PointSerializer,
               400: OpenApiResponse(description="Invalid data"),
               403: OpenApiResponse(description="You do not have permission to modify this route", examples={"application/json": {"error": "You do not have permission to modify this route"}}),
               404: OpenApiResponse(description="Route not found")},
    description="Create a new point in a route.",
    tags=["Routes"],
)
class PointCreateAPIView(APIView):
    serializer_class = PointSerializer

    def post(self, request, route_id):
        try:
            route = Route.objects.get(id=route_id)
        except Route.DoesNotExist:
            return Response({"error": "Route not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreatePointSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not route.can_modify(request.user):
            return Response({"error": "You do not have permission to modify this route"}, status=status.HTTP_403_FORBIDDEN)

        if not route.image.are_valid_coordinates(request.data['lat'], request.data['lon']):
            return Response({"error": "Invalid coordinates"}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(route=route, order=route.get_points().count() + 1)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@extend_schema(
    responses={
        200: PointSerializer,
        404: OpenApiResponse(description="Point or Route not found"),
        403: OpenApiResponse(description="You do not have permission to modify this route")
    },
    description="Get a point.",
    tags=["Routes"],
)
class PointAPIView(APIView):
    serializer_class = PointSerializer

    def get(self, request, route_id, point_id):
        try:
            route = Route.objects.get(id=route_id)
            point = route.get_points().filter(id=point_id).first()
            if not point:
                raise Point.DoesNotExist
        except Point.DoesNotExist:
            return Response({"error": "Point not found"}, status=status.HTTP_404_NOT_FOUND)
        except Route.DoesNotExist:
            return Response({"error": "Route not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(point)
        return Response(serializer.data)

@extend_schema(
    responses={
        204: OpenApiResponse(description="Point deleted"),
        403: OpenApiResponse(description="You do not have permission to modify this route"),
        404: OpenApiResponse(description="Point not found")
    },
    description="Delete a point.",
    tags=["Routes"],
)
class PointDeleteAPIView(APIView):
    def delete(self, request, route_id, point_id):
        try:
            route = Route.objects.get(id=route_id)
            point = Point.objects.get(id=point_id)
        except Point.DoesNotExist:
            return Response({"error": "Point not found"}, status=status.HTTP_404_NOT_FOUND)
        except Route.DoesNotExist:
            return Response({"error": "Route not found"}, status=status.HTTP_404_NOT_FOUND)

        if not route.can_modify(request.user):
            return Response({"error": "You do not have permission to modify this route"}, status=status.HTTP_403_FORBIDDEN)

        point.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)