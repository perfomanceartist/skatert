import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from users.models import AuthTokens, UserAuth


def check_token(nickname, tokenVal):
    user = UserAuth.objects.filter(nickname= nickname).get()
    if user is None:
        return False
    
    token = AuthTokens.objects.filter(user = user).filter(token = tokenVal).get() 
    if token is None:
        return False   

    if token.type != "email":
        return False
    
    if datetime.datetime.now().timestamp() > token.expiration_date.timestamp():
        token.delete()
        return False
     
    return True

def check_cookie(request):
    try:        
        nickname = request.COOKIES['nickname']
    except:
        return False
    
    try:
        token = request.COOKIES['token']
    except:
        return False
    return check_token(nickname,token) 
    
    


def index(request):
    return HttpResponse("Главная страница")
