from django.urls import path

from . import views

urlpatterns = [
    path("", views.list_maps_and_points),
    path("map/", views.create),
]