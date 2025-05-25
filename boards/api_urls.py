from django.urls import path
from .api_views import *

urlpatterns = [
    path('', create_background_view, name='api_create_background'),
    path('<uuid:board_id>', BoardViews.as_view(), name='api_edit_background'),
    path('', list_backgrounds_view, name='api_list_backgrounds'),
    path('my/', list_my_backgrounds_view, name='api_list_my_backgrounds'),
    path('<uuid:board_id>/solutions', create_solution_view, name='api_create_solution'),
    path('<uuid:board_id>/solutions/<uuid:solution_id>', edit_solution_view, name='api_edit_solution'),
]