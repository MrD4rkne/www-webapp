from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("points/", include("points.urls")),
    path("admin/", admin.site.urls),
]