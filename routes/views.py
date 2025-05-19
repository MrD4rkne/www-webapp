from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from .forms import RouteForm, CreatePointForm
from images.models import Image
import json
from django.core.serializers.json import DjangoJSONEncoder
from routes.models import Route, Point

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

    route_data = {
        'id': route.id,
        'name': route.name,
        'image_url': route.image.image.url,
        'image_width': route.image.image.width,
        'image_height': route.image.image.height,
        'author_id': route.author.id,
        'author_username': route.author.username,
    }

    points_data = [
        {
            'id': point.id,
            'lat': point.lat,
            'lon': point.lon,
            'order': point.order,
        } for point in points
    ]

    context = {
        'route': route,
        'points': points,
        'route_json': json.dumps(route_data, cls=DjangoJSONEncoder),
        'points_json': json.dumps(points_data, cls=DjangoJSONEncoder),
        'current_user': request.user
    }

    return render(request, 'routes/detail.html', context)

@require_http_methods(['POST'])
@login_required()
def delete_route(request, route_id):
    try:
        route = Route.objects.get(id=route_id)
    except Route.DoesNotExist:
        return HttpResponseNotFound("Route not found")

    if not route.can_modify(request.user):
        return HttpResponseForbidden("You do not have permission to modify this route")

    route.delete()
    return redirect('get_routes_view')

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
    point.order = route.points.count() + 1
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

@require_http_methods(['POST'])
@login_required()
def reorder_points(request, route_id):
    try:
        route = Route.objects.get(id=route_id)
    except Route.DoesNotExist:
        return HttpResponseNotFound("Route not found")

    if not route.can_modify(request.user):
        return HttpResponseForbidden("You do not have permission to modify this route")

    data = json.loads(request.body)

    if 'order' not in data:
        return HttpResponseBadRequest("Invalid data format")

    points = route.get_points()

    # Validate all data before saving
    new_orders = []
    for item in data.get('order', []):
        if 'id' in item and 'order' in item:
            point_id = item['id']
            new_order = item['order']
            point = points.filter(id=point_id).first()
            if not point:
                return HttpResponseNotFound(f"Point with id {point_id} not found")
            new_orders.append((point, new_order))
        else:
            return HttpResponseBadRequest("Invalid data format")

    # Validate points order
    order_set = set()
    for _, new_order in new_orders:
        if new_order in order_set:
            return HttpResponseBadRequest("Duplicate order values found")
        order_set.add(new_order)

    # Save points only if validation passes
    for point, new_order in new_orders:
        point.order = new_order
        point.save()

    route.save()

    return HttpResponse(status=204)