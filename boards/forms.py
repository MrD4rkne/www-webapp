from django import forms
from .models import GameBoard

MIN_BOARD_WIDTH = 1
MAX_BOARD_WIDTH = 2000
MIN_BOARD_HEIGHT = 1
MAX_BOARD_HEIGHT = 2000

class GameBoardForm(forms.ModelForm):
    """
    Form for creating and updating GameBoard objects with proper validation.
    """

    class Meta:
        model = GameBoard
        fields = ['name', 'columns', 'rows', 'points']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Board Name'}),
            'columns': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': MIN_BOARD_WIDTH,
                'max': MAX_BOARD_WIDTH,
                'placeholder': 'Width'
            }),
            'rows': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': MIN_BOARD_HEIGHT,
                'max': MAX_BOARD_HEIGHT,
                'placeholder': 'Height'
            }),
            'points': forms.HiddenInput(),
        }

    def clean_points(self):
        """Validate that points data is properly formatted and each color has exactly 2 points"""
        points = self.cleaned_data.get('points')

        game_board = GameBoard(points=points, columns=self.cleaned_data.get('columns', 1), rows=self.cleaned_data.get('rows', 1))
        try:
            game_board.validate_points()
        except ValueError as e:
            raise forms.ValidationError(str(e))

        return points

    def clean(self):
        """Ensure all points are within the grid dimensions"""
        cleaned_data = super().clean()
        points = cleaned_data.get('points')
        width = cleaned_data.get('width')
        height = cleaned_data.get('height')

        return cleaned_data