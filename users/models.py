import datetime
from django.db import models

class UserAuth(models.Model):
    nickname = models.CharField(max_length=32)
    passwordhash = models.CharField(max_length=16)
    email = models.EmailField()

class AuthTokens(models.Model):
    user = models.ForeignKey(UserAuth, on_delete=models.CASCADE)
    token = models.CharField(max_length=16, default = '')
    type = models.CharField(max_length=10, default='password')
    expiration_date = models.DateTimeField()
    
