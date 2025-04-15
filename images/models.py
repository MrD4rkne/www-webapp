from django.db import models
from django.conf import settings

class Image(models.Model):
    id = models.AutoField(primary_key=True),
    name = models.CharField(max_length=250,default="")
    image = models.ImageField(upload_to='images/')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
