from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .forms import RouteForm

from routes.models import Route

@login_required()
def create_route(request, image_id):
    if request.method == 'POST':
        form = RouteForm(request.POST, user=request.user)
        if form.is_valid():
            route = form.save(commit=False)
            route.author = request.user
            route.save()
            return render(request, 'routes/detail.html', {'route': route})
    else:
        form = RouteForm(user=request.user)
    return render(request , 'routes/create.html', {'form': form, 'current_user': request.user})


@require_http_methods(['GET'])
@login_required()
def get_routes_view(request):
    if not request.user.is_authenticated:
        return render(request, 'routes/error.html', {'error': 'User not authenticated'})
    print("User:", request.user)
    routes = Route.objects.filter(author=request.user)
    return render(request, 'routes/list.html', {'routes': routes, 'current_user': request.user})