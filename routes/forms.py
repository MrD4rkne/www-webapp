from django import forms
from images.models import Image
from routes.models import Route

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name', 'image']

    image = forms.ModelChoiceField(
        queryset=Image.objects.none(),
        label="Route Image",
        widget=forms.Select(attrs={
            'class': 'w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500'
        })
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['image'].queryset = Image.objects.filter(author=user)