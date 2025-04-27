from django.db import models
from images import models as img_models
from django.conf import settings

class Route(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, default="")
    image = models.ForeignKey(img_models.Image, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def can_modify(self, user):
        return self.author == user

    def get_points(self):
        return Point.objects.filter(route=self)

    def __str__(self):
        return self.name

class Point(models.Model):
    id = models.AutoField(primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    lat = models.IntegerField()
    lon = models.IntegerField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Point <{self.lat}, {self.lon}>"