from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import GameBoardForm
from .models import GameBoard


@login_required
def create_background_view(request):
    form = GameBoardForm()
    return render(request, 'boards/createEdit.html', {'form': form})

@login_required
def edit_background_view(request, board_id):
    try:
        game_board = GameBoard.objects.get(pk=board_id)

        if game_board.user != request.user:
            raise GameBoard.DoesNotExist()
    except GameBoard.DoesNotExist:
        raise Http404("Game board does not exist")

    form = GameBoardForm(instance=game_board)
    return render(request, 'boards/createEdit.html', {'form': form, 'game_board': game_board})

def list_backgrounds_view(request):
    game_boards = GameBoard.objects.all().defer('points')
    return render(request, 'boards/list.html', {'game_boards': game_boards})

@login_required
def list_my_backgrounds_view(request):
    game_boards = GameBoard.objects.defer('points').filter(user=request.user)
    return render(request, 'boards/list.html', {'game_boards': game_boards})

@login_required
def create_solution_view(request, board_id):
    try:
        game_board = GameBoard.objects.get(pk=board_id)

        if game_board.user != request.user:
            raise GameBoard.DoesNotExist()
    except GameBoard.DoesNotExist:
        raise Http404("Game board does not exist")

    return render(request, 'boards/solutions_createEdit.html', {'game_board': game_board})