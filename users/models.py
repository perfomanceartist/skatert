from django.contrib.postgres.fields import ArrayField
from django.db import models

from music.models import Track


class User(models.Model):
    nickname = models.CharField(max_length=50, blank=False, unique=True)
    lastfm = models.CharField(max_length=50, blank=True)
    favouriteTracks = models.ManyToManyField(Track, related_name='favouriteTracks')
    unfavouriteTracks = models.ManyToManyField(Track, related_name='unfavouriteTracks')
    recommenders = ArrayField(models.IntegerField(), default=list, primary_key=False, blank=False)
    subscriptions = ArrayField(models.IntegerField(), default=list, primary_key=False, blank=False)


class MusicPreferences(models.Model):
    "Запись вида Жанр - Битовая маска пользователей"
    genre = models.IntegerField(primary_key=True, blank=False)
    usersBitmask = ArrayField(models.BooleanField(), primary_key=False, blank=False)


class FilmsPreferences(models.Model):
    "Запись вида Жанр - Битовая маска пользователей"
    genre = models.IntegerField(primary_key=True, blank=False)
    usersBitmask = ArrayField(models.BooleanField(), primary_key=False, blank=False)


class BooksPreferences(models.Model):
    "Запись вида Жанр - Битовая маска пользователей"
    genre = models.IntegerField(primary_key=True, blank=False)
    usersBitmask = ArrayField(models.BooleanField(), primary_key=False, blank=False)





class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    passwordhash = models.CharField(max_length=64)
    email = models.EmailField()    
    secondFactor = models.BooleanField(default=False, blank=False)


class AuthTokens(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    token = models.CharField(max_length=16, default="")
    type = models.CharField(max_length=10, default="password")
    expiration_date = models.DateTimeField()
