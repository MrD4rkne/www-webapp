from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from images import models as img_models

from routes.models import Route

@require_http_methods(['POST'])
@login_required(login_url='/login/')
def post_route(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        image_id = request.POST.get('image_id', None)

        if not name or not image_id:
            return render(request, 'routes/error.html', {'error': 'Invalid data'})

        try:
            image = img_models.Image.objects.get(id=image_id, author=request.user)
        except img_models.Image.DoesNotExist:
            return render(request, 'routes/error.html', {'error': 'Image not found or not authorized'})

        route = Route.objects.create(name=name, image=image)
        return render(request, 'routes/detail.html', {'route': route})


@require_http_methods(['GET'])
@login_required(login_url='/login/')
def get_routes(request):
    if not request.user.is_authenticated:
        return render(request, 'routes/error.html', {'error': 'User not authenticated'})
    print("User:", request.user)
    routes = Route.objects.filter(author=request.user)
    return render(request, 'routes/list.html', {'routes': routes, 'current_user': request.user})