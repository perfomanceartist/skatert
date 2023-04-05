import datetime
from music.models import Track
from django.contrib.postgres.fields import ArrayField
from django.db import models


class UserAuth(models.Model):
    nickname = models.CharField(max_length=32)
    passwordhash = models.CharField(max_length=16)
    email = models.EmailField()


class AuthTokens(models.Model):
    user = models.ForeignKey(UserAuth, on_delete=models.CASCADE)
    token = models.CharField(max_length=16, default="")
    type = models.CharField(max_length=10, default="password")
    expiration_date = models.DateTimeField()


class User(models.Model):
    user = models.ForeignKey(UserAuth, on_delete=models.CASCADE)
    lastfm = models.CharField(max_length=50, blank=True)
    #favouriteMusic = ArrayField(models.IntegerField(), primary_key=False, blank=False)
    #favouriteFilms = ArrayField(models.IntegerField(), primary_key=False, blank=False)
    #favouriteBooks = ArrayField(models.IntegerField(), primary_key=False, blank=False)

class FavouriteTracks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)


class Subscriptions(models.Model):
    id = models.ForeignKey(User, primary_key=True, on_delete=models.CASCADE)
    subscriptions = ArrayField(models.IntegerField(), primary_key=False, blank=False)



class FilmsPreferences(models.Model):
    genre = models.IntegerField(primary_key=True, blank=False)
    usersBitmask = ArrayField(models.BooleanField(), primary_key=False, blank=False)


class BooksPreferences(models.Model):
    genre = models.IntegerField(primary_key=True, blank=False)
    usersBitmask = ArrayField(models.BooleanField(), primary_key=False, blank=False)
