from django.core import serializers
from rest_framework import serializers
from .models import GameBoard, Solution

MAX_BOARD_WIDTH = 1000
MAX_BOARD_HEIGHT = 1000


class ColorSerializer(serializers.Serializer):
    """
    Serializer for color validation.
    """
    hex_value = serializers.CharField(max_length=7)

    def validate_hex_value(self, value):
        """Ensure the hex value is a valid hex color code."""
        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError("Hex value must be a valid hex color code (e.g., #RRGGBB).")
        return value

class PathPointSerializer(serializers.Serializer):
    x = serializers.IntegerField(min_value=0)
    y = serializers.IntegerField(min_value=0)


class PathSerializer(serializers.Serializer):
    start = PathPointSerializer()
    end = PathPointSerializer()
    color = ColorSerializer()
    path = PathPointSerializer(many=True)

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



def _validate_paths_edges(paths, points):
    """Ensure that each path's start and end points match the board points."""
    for path in paths:
        color = path['color']['hex_value']
        start = (path['start']['x'], path['start']['y'])
        end = (path['end']['x'], path['end']['y'])

        # Verify start and end points match board points
        board_color_points = [(p['x'], p['y']) for p in points]
        if start not in board_color_points or end not in board_color_points:
            raise serializers.ValidationError(f"Path points don't match board points for color {color}")

        # Ensure path contains both endpoints
        path_points = [(p['x'], p['y']) for p in path['path']]
        if start not in path_points or end not in path_points:
            raise serializers.ValidationError(f"Path must include both start and end points")


def _validate_color_points(points, paths):
    colors = set()
    board_points = {}
    # Collect all points by color from the game board
    for point in points:
        color_hex = point['color']['hex_value']
        if color_hex not in board_points:
            board_points[color_hex] = []
        board_points[color_hex].append(point)

    # Check if each color is connected by exactly one path
    color_paths = {}
    for path in paths:
        color_hex = path['color']['hex_value']
        if color_hex not in color_paths:
            color_paths[color_hex] = []
        color_paths[color_hex].append(path)

    for color, paths in color_paths.items():
        if len(paths) != 1:
            raise serializers.ValidationError(f"Color {color} must have exactly one path.")
        colors.add(color)


def _validate_path_continuity(path):
    """Ensure that the path is continuous and does not skip points."""
    points = path['path']
    if len(points) < 2:
        raise serializers.ValidationError("Path must have at least two points.")

    for i in range(len(points) - 1):
        diff = abs(points[i]['x'] - points[i + 1]['x']) + abs(points[i]['y'] - points[i + 1]['y'])
        if diff != 1:
            raise serializers.ValidationError("Path must be continuous, with each point adjacent to the next.")


def _do_paths_cross(path1, path2):
    """Check if two paths cross each other."""
    for i in range(len(path1) - 1):
        seg1_start = path1[i]
        seg1_end = path1[i + 1]

        for j in range(len(path2) - 1):
            seg2_start = path2[j]
            seg2_end = path2[j + 1]

            # Check for segment intersection similar to doSegmentsIntersect in JS
            # This is a simplified check for orthogonal segments only
            if (seg1_start['x'] == seg1_end['x'] and seg2_start['y'] == seg2_end['y']  # one vertical, one horizontal
                or seg1_start['y'] == seg1_end['y'] and seg2_start['x'] == seg2_end['x']):

                if seg1_start['x'] == seg1_end['x']:  # First segment is vertical
                    x = seg1_start['x']
                    min_y = min(seg1_start['y'], seg1_end['y'])
                    max_y = max(seg1_start['y'], seg1_end['y'])

                    y = seg2_start['y']
                    min_x = min(seg2_start['x'], seg2_end['x'])
                    max_x = max(seg2_start['x'], seg2_end['x'])

                    if min_x <= x <= max_x and min_y <= y <= max_y:
                        return True
                else:  # First segment is horizontal
                    y = seg1_start['y']
                    min_x = min(seg1_start['x'], seg1_end['x'])
                    max_x = max(seg1_start['x'], seg1_end['x'])

                    x = seg2_start['x']
                    min_y = min(seg2_start['y'], seg2_end['y'])
                    max_y = max(seg2_start['y'], seg2_end['y'])

                    if min_x <= x <= max_x and min_y <= y <= max_y:
                        return True

    return False


class SolutionSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating solutions for a GameBoard.
    """
    game_board = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    paths = PathSerializer(many=True)
    name = serializers.CharField(max_length=255, required=True)

    class Meta:
        model = Solution
        fields = ['id', 'game_board', 'user', 'paths', 'name']
        read_only_fields = ['id', 'game_board', 'user']

    def validate(self, data):
        """Validate the entire solution."""
        board = self.instance.game_board if self.instance else self.context['game_board']
        paths = data.get('paths', [])

        for path in paths:
            _validate_path_continuity(path)
        _validate_color_points(board.points, paths)
        _validate_paths_edges(paths, board.points)

        # Check for path crossings
        for i, path1 in enumerate(paths):
            for j, path2 in enumerate(paths):
                if i >= j:
                    continue  # Skip self-comparisons and duplicates

                if _do_paths_cross(path1['path'], path2['path']):
                    raise serializers.ValidationError(
                        f"Paths for colors {path1['color']['hex_value']} and {path2['color']['hex_value']} cross each other"
                    )

        return data

