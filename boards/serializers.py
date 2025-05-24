from django import forms
from .models import GameBoard, ColorPoints


from rest_framework import serializers
from .models import GameBoard, ColorPoints

MAX_BOARD_WIDTH = 1000
MAX_BOARD_HEIGHT = 1000


class ColorSerializer(serializers.Serializer):
    """
    Serializer for color validation.
    """
    name = serializers.CharField(max_length=100)
    hex_value = serializers.CharField(max_length=7)

    def validate_hex_value(self, value):
        """Ensure the hex value is a valid hex color code."""
        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError("Hex value must be a valid hex color code (e.g., #RRGGBB).")
        return value


class PointWithColorSerializer(serializers.Serializer):
    color = ColorSerializer()

    x = serializers.IntegerField(min_value=0, max_value=MAX_BOARD_WIDTH - 1)
    y = serializers.IntegerField(min_value=0, max_value=MAX_BOARD_HEIGHT - 1)

class GameBoardSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating GameBoard objects with proper validation.
    """

    points = PointWithColorSerializer(many=True)

    class Meta:
        model = GameBoard
        fields = ['id','name', 'columns', 'rows', 'points']
        extra_kwargs = {
            'id': {'read_only': True},
            'columns': {'min_value': 0, 'max_value': MAX_BOARD_WIDTH},
            'rows': {'min_value': 0, 'max_value': MAX_BOARD_HEIGHT},
        }

    def validate_points(self, points):
        """Validate that points data is properly formatted and each color has exactly 2 points"""
        game_board = GameBoard(
            points=points,
            columns=self.initial_data.get('columns', 1),
            rows=self.initial_data.get('rows', 1)
        )
        try:
            game_board.validate_points()
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        return points

    def validate(self, data):
        """Ensure all points are within the grid dimensions."""
        points = data.get('points', [])
        width = data.get('columns')
        height = data.get('rows')

        for point in points:
            if not (0 <= point['x'] < width) or not (0 <= point['y'] < height):
                raise serializers.ValidationError(
                    f"Point ({point['x']}, {point['y']}) is out of bounds for the grid dimensions ({width}x{height})."
                )

        return data