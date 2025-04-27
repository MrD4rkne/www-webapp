from common.serializers import UserSerializer
from images.serializers import ImageSerializer
from rest_framework import serializers
from .models import Route, Point

class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['id', 'lat', 'lon', 'order']
        extra_kwargs = {
            'lat': {'required': True},
            'lon': {'required': True},
            'order': {'required': True}
        }

class CreatePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['lat', 'lon']
        extra_kwargs = {
            'lat': {'required': True},
            'lon': {'required': True},
            'order': {'required': False}
        }

class RouteDetailsSerializer(serializers.ModelSerializer):
    points = PointSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    image = ImageSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'name', 'image', 'author', 'points']
        extra_kwargs = {
            'author': {'read_only': True},
            'image': {'required': True}
        }

class RouteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = ImageSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'name', 'image', 'author']
        extra_kwargs = {
            'author': {'read_only': True},
            'image': {'required': True}
        }

class RouteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['name', 'image']
        extra_kwargs = {
            'name': {'required': True},
            'image': {'required': True}
        }