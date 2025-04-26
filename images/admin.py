from django.contrib import admin
from .models import Image

class ImageAdmin(admin.ModelAdmin):
    exclude = ('author',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
        obj.horizontal_resolution = form.cleaned_data.get('horizontal_resolution')
        super().save_model(request, obj, form, change)

admin.site.register(Image, ImageAdmin)
