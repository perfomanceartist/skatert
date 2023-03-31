import datetime
import json
from random import randint

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from users.models import AuthTokens, UserAuth


def index(request):
    return HttpResponse("API")

@csrf_exempt
def register(request):
    if request.method == "POST":
        try:            
            data = json.loads(request.body.decode('utf-8'))
        except:
            return HttpResponseBadRequest("Некорректный формат данных") 
        nickname = data['nickname']      
        if nickname is None:
            return HttpResponseBadRequest("Не указан nickname") 
        email = data['email']
        if email is None:
            return HttpResponseBadRequest("Не указан email")
        
        hash = data['hash']
        if hash is None:
            return HttpResponseBadRequest("Не указан хеш пароля") 
        
        user = UserAuth(nickname = nickname, email=email, passwordhash = hash)
        user.save()
        return HttpResponse("Registered")
    else:
        return HttpResponseBadRequest("Некорректный метод запроса")

@csrf_exempt
def password_auth(request):
    if request.method == "POST":
        try:            
            data = json.loads(request.body.decode('utf-8'))
        except:
            return HttpResponseBadRequest("Некорректный формат данных")
        
        nickname = data['nickname'] 
        if nickname is None:
            return HttpResponseBadRequest("Не указан nickname") 
        hash = data['hash'] 
        if hash is None:
            return HttpResponseBadRequest("Не указан email") 
        
        try:
            user = UserAuth.objects.filter(nickname = nickname).filter(passwordhash = hash).get()
        except:
            return HttpResponseBadRequest("Неверные учетные данные") 
        if user is None:
            return HttpResponseBadRequest("Неверные учетные данные") 
        
        token = str(randint(100000, 999999))
        hashToken = AuthTokens(user = user, token = token, type='hash', expiration_date = datetime.datetime.now() + datetime.timedelta(minutes = 15))
        hashToken.save()

      
        send_mail( 'Skatert. Код Подтверждения входа', #subject
                  f'Код подтверждения для входа в Skatert: {token}', #message
                  settings.EMAIL_HOST_USER, 
                  [user.email, ], 
                  fail_silently=False
                )



        return HttpResponse("Token: " + token)
    else:
        return HttpResponseBadRequest("Некорректный метод запроса")

@csrf_exempt
def email_auth(request):
    if request.method == "POST":
        try:            
            data = json.loads(request.body.decode('utf-8'))
        except:
            return HttpResponseBadRequest("Некорректный формат данных")
        
        nickname = data['nickname'] 
        if nickname is None:
            return HttpResponseBadRequest("Не указан nickname") 
        code = data['code'] 
        if code is None:
            return HttpResponseBadRequest("Не указан email") 


        user = UserAuth.objects.filter(nickname= nickname).get()
        if user is None:
            return HttpResponseBadRequest("Некорректные данные") 
        
        token = AuthTokens.objects.filter(user = user).filter(token = code).get()
        if token is None:
            return False          
        if datetime.datetime.now().timestamp() > token.expiration_date.timestamp():
            token.delete()
            return HttpResponseBadRequest("Токен не актуален. Попробуйте ещё раз.") 

        token.token = hex(randint(100, 0xFFFFFFFF))
        token.type = "email"
        token.expiration_date = datetime.datetime.now() + datetime.timedelta(days=1)
        token.save()
        response = JsonResponse({"token": str(token.token)})
        response.set_cookie('token', str(token.token))
        response.set_cookie('nickname', nickname)
        return response
    else:
        return HttpResponseBadRequest("Некорректный метод запроса")
