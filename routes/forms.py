from django import forms
from routes.models import Route, Point

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

from django.core.exceptions import ValidationError

class CreatePointForm(forms.ModelForm):
    class Meta:
        model = Point
        fields = ['lat', 'lon']

    def __init__(self, *args, **kwargs):
        self.image = kwargs.pop('image', None)
        super().__init__(*args, **kwargs)

    def clean_lat(self):
        lat = self.cleaned_data.get('lat')
        if lat is None:
            raise ValidationError("Latitude must be between set.")
        return lat

    def clean_lon(self):
        lon = self.cleaned_data.get('lon')
        if lon is None:
            raise ValidationError("Longitude must be between set.")
        return lon

    def clean(self):
        cleaned_data = super().clean()
        lat = self.clean_lat()
        lon = self.clean_lon()

        if self.image and not self.image.are_valid_coordinates(lat, lon):
            raise ValidationError("Invalid latitude or longitude for this image.")

        return cleaned_data