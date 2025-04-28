from django.shortcuts import render
from django.http import FileResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.conf import settings
import os
from os.path import isfile, join
from images.models import Image

def get_index(request):
    return render(request, 'index.html')

def protected_media(request, path):
    media_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(media_path):
        return HttpResponseNotFound("Media file not found")

    img = Image.objects.filter(image=path).first()
    if img:
        if not img.is_public and (request.user.is_authenticated or img.author != request.user):
            return HttpResponseNotFound("Media file not found")

    return FileResponse(open(media_path, 'rb'))