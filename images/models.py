from django.db import models
from django.conf import settings

class Image(models.Model):
    id = models.AutoField(primary_key=True),
    name = models.CharField(max_length=250,default="")
    image = models.ImageField(upload_to='images/')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)

    def can_access(self, user):
        if self.is_public:
            return True
        return self.author == user

    def are_valid_coordinates(self, x, y):
        return self.image.height >= y >= 0 and self.image.width >= x >= 0

    def __str__(self):
        return self.name
