from rest_framework import serializers
from .models import Route, Point

class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['id', 'latitude', 'longitude', 'order']

class RouteSerializer(serializers.ModelSerializer):
    points = PointSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'name', 'image', 'author', 'points']

class RouteWithoutPointsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ['id', 'name', 'image', 'author']