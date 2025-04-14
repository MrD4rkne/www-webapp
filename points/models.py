from django.db import models

class Map(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

class Point(models.Model):
    map=models.ForeignKey(Map, on_delete=models.CASCADE)
