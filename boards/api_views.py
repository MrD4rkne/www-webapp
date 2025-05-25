import uuid
from uuid import UUID

from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import GameBoard, Solution
from .serializers import GameBoardSerializer, SolutionSerializer


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
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
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

class BoardViews(APIView):
    @extend_schema(
        request=GameBoardSerializer,
        responses={
            200: GameBoardSerializer,
            400: OpenApiResponse(description="Invalid data"),
            404: OpenApiResponse(description="Game board not found"),
        },
        description="Update an existing game board.",
        tags=["Game Boards"]
    )
    def put(self, request, board_id):
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
        responses={
            204: OpenApiResponse(description="Game board deleted"),
            404: OpenApiResponse(description="Game board not found"),
        },
        description="Delete a specific game board.",
        tags=["Game Boards"]
    )
    def delete(self, request, board_id):
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
        description="Retrieve details of a specific game board.",
        tags=["Game Boards"]
    )
    def get(self, request, board_id):
        try:
            game_board = GameBoard.objects.get(pk=board_id)
            if game_board.user != request.user:
                raise GameBoard.DoesNotExist()
        except GameBoard.DoesNotExist:
            return Response({"error": "Game board not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = GameBoardSerializer(game_board)
        return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(
    responses={
        200: SolutionSerializer,
        404: OpenApiResponse(description="Game board not found")
    },
    request=SolutionSerializer,
    description="Create solution.",
    tags=["Solutions"]
)
@api_view(['POST'])
def create_solution_view(request, board_id):
    try:
        game_board = GameBoard.objects.get(pk=board_id)
    except GameBoard.DoesNotExist:
        return Response({"error": "Game board not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = SolutionSerializer(data=request.data, context={'game_board': game_board, 'user': request.user})
    if serializer.is_valid():
        serializer.save(game_board=game_board, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    request=SolutionSerializer,
    responses={
        200: SolutionSerializer,
        404: OpenApiResponse(description="Game board or solution not found"),
        400: OpenApiResponse(description="Invalid data")
    },
    description="Edit an existing solution.",
    tags=["Solutions"]
)
@api_view(['PUT'])
def edit_solution_view(request, board_id, solution_id):
    try:
        game_board = GameBoard.objects.get(pk=board_id)
    except GameBoard.DoesNotExist:
        return Response({"error": "Game board not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        solution = Solution.objects.get(pk=solution_id, game_board=game_board)
        if solution.user != request.user:
            raise Solution.DoesNotExist()
    except Solution.DoesNotExist:
        return Response({"error": "Solution not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = SolutionSerializer(solution, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)