from rest_framework import serializers
from .models import Image
from common.serializers import UserSerializer

class ImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj) -> str:
        return obj.image.url if obj.image else None

    class Meta:
        model = Image
        fields = ['id', 'name', 'url', 'is_public']

class ImageDetailsSerializer(ImageSerializer):
    author = UserSerializer(read_only=True)

    class Meta(ImageSerializer.Meta):
        fields = ImageSerializer.Meta.fields + ['author']
        extra_kwargs = {
            'author': {'read_only': True},
            'is_public': {'required': True}
        }