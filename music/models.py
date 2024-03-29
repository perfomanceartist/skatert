from django.contrib.postgres.fields import ArrayField
from django.db import models

IMAGE_PATH_MAXIMUM_SIZE = 256
OBJECT_NAME_MAXIMUM_SIZE = 150


class Artist(models.Model):
    name = models.CharField(max_length=OBJECT_NAME_MAXIMUM_SIZE)
    img_small = models.CharField(max_length=IMAGE_PATH_MAXIMUM_SIZE)
    img_medium = models.CharField(max_length=IMAGE_PATH_MAXIMUM_SIZE)
    img_large = models.CharField(max_length=IMAGE_PATH_MAXIMUM_SIZE)
    listeners = models.PositiveBigIntegerField(default=1)


class Album(models.Model):
    name = models.CharField(max_length=OBJECT_NAME_MAXIMUM_SIZE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    img_small = models.CharField(max_length=IMAGE_PATH_MAXIMUM_SIZE)
    img_medium = models.CharField(max_length=IMAGE_PATH_MAXIMUM_SIZE)
    img_large = models.CharField(max_length=IMAGE_PATH_MAXIMUM_SIZE)
    listeners = models.PositiveBigIntegerField(default=1)


class Track(models.Model):
    name = models.CharField(max_length=OBJECT_NAME_MAXIMUM_SIZE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, blank=True, null=True)
    genres = ArrayField(models.BooleanField(), default=list, blank=True)
    lovers = models.PositiveBigIntegerField(default=1, blank=False)
    recommended = models.PositiveBigIntegerField(default=0, blank=False)
