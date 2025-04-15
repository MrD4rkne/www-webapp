from django.http import HttpResponse

from images.models import Image
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

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
    return HttpResponse(img.image.url, status=200)

@require_http_methods(['GET'])
def get_images(request):
    imgs = Image.objects.filter(is_public=True)
    if request.user.is_authenticated:
        imgs = imgs | Image.objects.filter(author=request.user)
    imgs = imgs.values_list('image', flat=True)
    return HttpResponse(imgs, status=200)

