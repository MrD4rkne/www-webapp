from django.http import HttpResponse

from django.core.files.storage import FileSystemStorage
from images.models import Image
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

@require_http_methods(['GET'])
@login_required
def get_image(request, image_id):
    try:
        img = Image.objects.get(id=image_id)
    except Image.DoesNotExist:
        return HttpResponse("Image not found", status=404)

    if img.author != request.user:
        return HttpResponse("Image not found", status=404)

@require_http_methods(['GET'])
@login_required
def get_images(request, image_id):
    imgs = Image.objects.filter(author=request.user)
    return HttpResponse(imgs, status=200)

