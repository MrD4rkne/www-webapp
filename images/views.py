from django.http import HttpResponse
from django.shortcuts import render

from images.models import Image
from django.views.decorators.http import require_http_methods

@require_http_methods(['GET'])
def get_image(request, image_id):
    try:
        img = Image.objects.get(id=image_id)
    except Image.DoesNotExist:
        return HttpResponse("Image not found", status=404)

    if not img.is_public:
        # Check if logged-in user is the author
        if not request.user.is_authenticated or img.author != request.user:
            return HttpResponse("Image not found", status=404)
    return render(request, 'images/detail.html', {'image': img})

@require_http_methods(['GET'])
def get_images(request):
    images = Image.objects.filter(is_public=True)
    if request.user.is_authenticated:
        images = images | Image.objects.filter(author=request.user)
    return render(request, 'images/list.html', {'images': images, 'current_user': request.user})

