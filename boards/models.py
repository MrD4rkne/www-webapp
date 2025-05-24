import uuid

from django.db import models

class Point:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return f"Point({self.x}, {self.y})"

    class Meta:
        verbose_name = 'Point'
        verbose_name_plural = 'Points'
        ordering = ['x', 'y']

    def validate(self):
        if not isinstance(self.x, int) or not isinstance(self.y, int):
            raise ValueError("Coordinates must be integers.")
        if self.x < 0 or self.y < 0:
            raise ValueError("Coordinates must be non-negative integers.")

class Color:
    name: str
    hex_value: str

    def __init__(self, name: str, hex_value: str):
        self.name = name
        self.hex_value = hex_value

    def __str__(self):
        return f"Color({self.name}, {self.hex_value})"

    class Meta:
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'
        ordering = ['name']

    def validate(self):
        if not isinstance(self.name, str) or not isinstance(self.hex_value, str):
            raise ValueError("Color name and hex value must be strings.")
        if not self.hex_value.startswith('#') or len(self.hex_value) != 7:
            raise ValueError("Hex value must be a valid hex color code (e.g., #RRGGBB).")

class ColorPoints(Point):
    color: Color

    def __init__(self, x: int, y: int, color: Color):
        super().__init__(x, y)
        self.color = color

    def __str__(self):
        return f"ColorPoints({self.x}, {self.y}, {self.color})"

    def validate(self):
        super().validate()
        self.color.validate()
        if not isinstance(self.color, Color):
            raise ValueError("Color must be an instance of the Color class.")

NUMBER_OF_POINTS_PER_COLOR = 2

class GameBoard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='game_boards'
    )
    points = models.JSONField(default=list, blank=True)
    columns = models.PositiveIntegerField(default=1)
    rows = models.PositiveIntegerField(default=1)

    def validate_points(self):
        if not isinstance(self.points, list):
            raise ValueError("There must be a non empty list of colored points.")
        color_count = {}
        for point in self.points:
            colorPoint = ColorPoints(
                x=point['x'],
                y=point['y'],
                color=Color(name=point['color']['name'], hex_value=point['color']['hex_value'])
            )
            colorPoint.validate()

            if colorPoint.x < 0 or colorPoint.x >= self.columns:
                raise ValueError(f"Point {colorPoint} is out of bounds for columns {self.columns}.")
            if colorPoint.y < 0 or colorPoint.y >= self.rows:
                raise ValueError(f"Point {colorPoint} is out of bounds for rows {self.rows}.")

        for color, count in color_count.items():
            if not count == NUMBER_OF_POINTS_PER_COLOR:
                raise ValueError(f"{color} has invalid number of points. Each color must have exactly {NUMBER_OF_POINTS_PER_COLOR} points.")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Game Board'
        verbose_name_plural = 'Game Boards'
        ordering = ['-id']