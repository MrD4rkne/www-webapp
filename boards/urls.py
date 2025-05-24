from django.urls import path
from .views import create_background_view, list_backgrounds_view, list_my_backgrounds_view, edit_background_view

urlpatterns = [
    path('create/', create_background_view, name='create_background'),
    path('edit/<uuid:board_id>/', edit_background_view, name='edit_background'),
    path('', list_backgrounds_view, name='list_backgrounds'),
    path('my/', list_my_backgrounds_view, name='list_my_backgrounds')
]
