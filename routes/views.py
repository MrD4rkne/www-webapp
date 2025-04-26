from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest
from .forms import RouteForm, CreatePointForm
from images.models import Image

from routes.models import Route

@require_http_methods(['GET', 'POST'])
@login_required()
def create_route_view(request, image_id):
    try:
        image = Image.objects.get(id=image_id)
        if not image.can_access(request.user):
            raise Image.DoesNotExist
    except Image.DoesNotExist:
        return HttpResponseNotFound("Image not found")

    if request.method == 'POST':
        form = RouteForm(request.POST, user=request.user)
        if form.is_valid():
            route = form.save(commit=False)
            route.author = request.user
            route.image = image
            route.save()
            return redirect('get_route_view', route_id=route.id)
    else:
        form = RouteForm(user=request.user)
    return render(request, 'routes/create.html', {'form': form, 'current_user': request.user, 'image': image})


@require_http_methods(['GET'])
@login_required()
def get_routes_view(request):
    routes = Route.objects.filter(author=request.user)
    return render(request, 'routes/list.html', {'routes': routes, 'current_user': request.user})

@require_http_methods(['GET'])
@login_required()
def get_route_view(request, route_id):
    try:
        route = Route.objects.get(id=route_id)
    except Route.DoesNotExist:
        return HttpResponseNotFound("Route not found")

    points = route.get_points()
    return render(request, 'routes/detail.html', {'route': route, 'points': points, 'current_user': request.user})

@require_http_methods(['POST'])
@login_required()
def create_point(request, route_id):
    try:
        route = Route.objects.get(id=route_id)
    except Route.DoesNotExist:
        return HttpResponseNotFound("Route not found")

    if not route.can_modify(request.user):
        return HttpResponseForbidden("You do not have permission to modify this route")

    form = CreatePointForm(request.POST, image=route.image)
    if not form.is_valid():
        return HttpResponseBadRequest(form.errors.as_json())

    point = form.save(commit=False)
    point.route = route
    point.save()

    return redirect('get_route_view', route_id=route.id)

@require_http_methods(['POST'])
@login_required()
def delete_point(request, route_id, point_id):
    try:
        route = Route.objects.get(id=route_id)
    except Route.DoesNotExist:
        return HttpResponseNotFound("Route not found")

    if not route.can_modify(request.user):
        return HttpResponseForbidden("You do not have permission to modify this route")

    point = route.get_points().filter(id=point_id)
    if not point.exists():
        return HttpResponseNotFound("Point not found")

    point.delete()
    return redirect('get_route_view', route_id=route.id)