from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("images/", include("images.urls")),
    path("routes/", include("routes.urls")),
    path('api/routes', include('routes.api_urls')),
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("", views.get_index, name="home")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)