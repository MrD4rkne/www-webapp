from django.urls import path
from .views import *

urlpatterns = [
    path('create/', create_background_view, name='create_background'),
    path('edit/<uuid:board_id>/', edit_background_view, name='edit_background'),
    path('', list_backgrounds_view, name='list_backgrounds'),
    path('my/', list_my_backgrounds_view, name='list_my_backgrounds'),
    path('<uuid:board_id>/solutions/create/', create_solution_view, name='create_solution'),
    path('<uuid:board_id>/solutions/<uuid:solution_id>/edit/', edit_solution_view, name='edit_solution'),
    path('solutions/', list_solutions_view, name='list_solutions'),
]
