from django.contrib import admin
from .models import GameBoard


@admin.register(GameBoard)
class GameBoardAdmin(admin.ModelAdmin):
    list_display = ['name', 'columns', 'rows']
    search_fields = ['name']
    list_filter = ['columns', 'rows']
    readonly_fields = ['name', 'columns', 'rows', 'points', 'user']