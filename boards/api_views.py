from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import GameBoard
from .serializers import GameBoardSerializer


@extend_schema(
    request=GameBoardSerializer,
    responses={
        201: GameBoardSerializer,
        400: OpenApiResponse(description="Invalid data")
    },
    description="Create a new game board.",
    tags=["Game Boards"]
)
@api_view(['POST'])
def create_background_view(request):
    serializer = GameBoardSerializer(data=request.data)
    if serializer.is_valid():
        game_board = serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    request=GameBoardSerializer,
    responses={
        200: GameBoardSerializer,
        400: OpenApiResponse(description="Invalid data"),
        404: OpenApiResponse(description="Game board not found"),
    },
    description="Edit an existing game board.",
    tags=["Game Boards"]
)
@api_view(['PUT'])
def edit_background_view(request, board_id):
    try:
        game_board = GameBoard.objects.get(pk=board_id)
        if game_board.user != request.user:
            raise GameBoard.DoesNotExist()
    except GameBoard.DoesNotExist:
        return Response({"error": "Game board not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = GameBoardSerializer(game_board, data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    responses={200: GameBoardSerializer(many=True)},
    description="List all game boards.",
    tags=["Game Boards"]
)
@api_view(['GET'])
def list_backgrounds_view(request):
    game_boards = GameBoard.objects.all()
    serializer = GameBoardSerializer(game_boards, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    responses={200: GameBoardSerializer(many=True)},
    description="List all game boards for the current user.",
    tags=["Game Boards"]
)
@api_view(['GET'])
def list_my_backgrounds_view(request):
    game_boards = GameBoard.objects.filter(user=request.user)
    serializer = GameBoardSerializer(game_boards, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    responses={
        404: OpenApiResponse(description="Game board not found"),
        204: OpenApiResponse(description="Game board deleted"),
    },
    description="Delete a game board.",
    tags=["Game Boards"]
)
@api_view(['DELETE'])
def delete_background_view(request, board_id):
    try:
        game_board = GameBoard.objects.get(pk=board_id)
        if game_board.user != request.user:
            raise GameBoard.DoesNotExist()
    except GameBoard.DoesNotExist:
        return Response({"error": "Game board not found"}, status=status.HTTP_404_NOT_FOUND)

    game_board.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(
    responses={
        200: GameBoardSerializer,
        404: OpenApiResponse(description="Game board not found")
    },
    description="Get details of a specific game board.",
    tags=["Game Boards"]
)
@api_view(['GET'])
def get_background_view(request, board_id):
    try:
        game_board = GameBoard.objects.get(pk=board_id)
        if game_board.user != request.user:
            raise GameBoard.DoesNotExist()
    except GameBoard.DoesNotExist:
        return Response({"error": "Game board not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = GameBoardSerializer(game_board)
    return Response(serializer.data, status=status.HTTP_200_OK)