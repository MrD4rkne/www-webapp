from django.urls import path
from .api_views import *

urlpatterns = [
    path('create/', create_background_view, name='api_create_background'),
    path('edit/<uuid:board_id>/', edit_background_view, name='api_edit_background'),
    path('', list_backgrounds_view, name='api_list_backgrounds'),
    path('my/', list_my_backgrounds_view, name='api_list_my_backgrounds'),
    path('<uuid:board_id>/', get_background_view, name='api_get_background'),
    path('delete/<uuid:board_id>/', delete_background_view, name='api_delete_background'),

]