from rest_framework import serializers
from .models import Image
from common.serializers import UserSerializer

class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    width = serializers.SerializerMethodField()
    height = serializers.SerializerMethodField()

    def get_url(self, obj) -> str:
        return obj.image.url if obj.image else None

    def get_width(self, obj) -> int:
        return obj.image.width if obj.image else None

    def get_height(self, obj) -> int:
        return obj.image.height if obj.image else None

    class Meta:
        model = Image
        fields = ['id', 'name', 'url', 'is_public', 'width', 'height']

class ImageDetailsSerializer(ImageSerializer):
    author = UserSerializer(read_only=True)

    class Meta(ImageSerializer.Meta):
        fields = ImageSerializer.Meta.fields + ['author']
        extra_kwargs = {
            'author': {'read_only': True},
            'is_public': {'required': True}
        }