from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Image
from drf_spectacular.utils import extend_schema, OpenApiResponse
from images.serializers import ImageSerializer, ImageDetailsSerializer

class ImageListAPIView(APIView):
    permission_classes = []
    @extend_schema(
        responses={200: ImageSerializer(many=True)},
        description="List all available images.",
        tags=["Images"])
    def get(self, request):
        images = Image.objects.filter(is_public=True)
        if request.user.is_authenticated:
            images = images | Image.objects.filter(author=request.user)

        serializer = ImageSerializer(images, many=True)
        return Response(serializer.data)

class ImageGetAPIView(APIView):
    permission_classes = []
    @extend_schema(
        responses={200: ImageDetailsSerializer(many=True),
                   404: OpenApiResponse(description="Image not found")},
        description="Get image",
        tags=["Images"])
    def get(self, request, image_id):
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response({"error": "Image not found"}, status=404)

        if not image.is_public and ( not request.user.is_authenticated or request.user != image.author):
            return Response({"error": "Image not found"}, status=404)

        serializer = ImageDetailsSerializer(image)
        return Response(serializer.data)
