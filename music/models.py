from django.db import models
from django.contrib.postgres.fields import ArrayField

class Artist(models.Model):
    name = models.CharField(max_length=50)
    img_small = models.CharField(max_length=100)
    img_medium = models.CharField(max_length=100)
    img_large = models.CharField(max_length=100)
    rating = models.PositiveBigIntegerField(default=1)


class Album(models.Model):
    name = models.CharField(max_length=50)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    img_small = models.CharField(max_length=100)
    img_medium = models.CharField(max_length=100)
    img_large = models.CharField(max_length=100)
    rating = models.PositiveBigIntegerField(default=1)

class Track(models.Model):
    name = models.CharField(max_length=50)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album =  models.ForeignKey(Album, on_delete=models.CASCADE)
    #img_small = models.CharField(max_length=100)
    #img_medium = models.CharField(max_length=100)
    #img_large = models.CharField(max_length=100)
    rating = models.PositiveBigIntegerField(default=1)
    
