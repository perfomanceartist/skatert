import datetime
import json
import re
from random import randint

from django.conf import settings
from django.core.mail import send_mail
from django.http import (HttpResponse, HttpResponseBadRequest, HttpResponseForbidden,
                         HttpResponseRedirect, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from backend.auth import check_cookie

import music.lastfm_api
from users.models import Account, AuthTokens, MusicPreferences, User


def index(request):
    return HttpResponse("API")


def _check_email(email: str):
    regex = re.compile(r"([a-zA-Z0-9]+[._-])*[a-zA-Z0-9]+@[a-zA-Z0-9]+(\.[A-Z|a-z]{2,})+")
    if re.fullmatch(regex, email):
        return True
    return False


class Register(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['nickname', 'email', 'hash'],
            properties={
                'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                'lastfm_nickname': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'hash': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description='OK'),
            400: openapi.Response(description='Bad request'),
            500: openapi.Response(description='Internal server error'),
        },
        operation_description='Register Skatert Account',
        tags=['Users']
    )
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            errorResponse = JsonResponse({
                "error": {
                    "code": 400,
                    "description": "Некорректный формат данных"
                }                
            })
            errorResponse.status_code=400 # BadRequest
            return errorResponse

        nickname = data.get("nickname")
        lastfm_nickname = data.get("lastfm_nickname", "-")

        if not nickname:
            errorResponse = JsonResponse({
                "error": {
                    "code": 223,
                    "description": "User is not specified"
                }                
            })
            errorResponse.status_code=400 # BadRequest
            return errorResponse
        email = data.get("email")
        if not email:
            errorResponse = JsonResponse({
                "error": {
                    "code": 223,
                    "description": "Email is not specified"
                }                
            })
            errorResponse.status_code=400 # BadRequest
            return errorResponse
        hash = data.get("hash")
        if not hash:
            errorResponse = JsonResponse({
                "error": {
                    "code": 223,
                    "description": "Hash is not specified"
                }                
            })
            errorResponse.status_code=400 # BadRequest
            return errorResponse

        if User.objects.filter(nickname=nickname).exists():
            errorResponse = JsonResponse({
                "error": {
                    "code": 222,
                    "description": "Such user already exists"
                }                
            })
            errorResponse.status_code=400 # BadRequest
            return errorResponse
            
        if not _check_email(email):
            errorResponse = JsonResponse({
                "error": {
                    "code": 225,
                    "description": "Bad email format"
                }                
            })
            errorResponse.status_code=400 # BadRequest
            return errorResponse
        
        

        user = User(nickname=nickname, lastfm=lastfm_nickname)
        user.save()
        account = Account(user=user, email=email, passwordhash=hash)
        account.save()

        music_prefs = MusicPreferences.objects.all()
        for music_pref in music_prefs:
            music_pref.usersBitmask += [False]
            music_pref.save()

        AuthToken = create_email_token(account)
        response = JsonResponse({
            "error": {
                    "code": 0,
                    "description": "Successfully Registered"
            }   
        })
        response.set_cookie("token", str(AuthToken.token))
        response.set_cookie("nickname", nickname)
        return response


def _email_request(account):
    token = create_hash_token(account)

    message =  f"Уважаемый {account.user.nickname}! \nКод подтверждения для входа в Skatert: {token}. Код действителен в течение 15 минут. \n\nС уважением, \nВаша Skatert"
    send_mail(
        "Skatert. Код подтверждения входа",  # subject
        message,  # message
        settings.EMAIL_HOST_USER,
        [
            account.email,
        ],
        fail_silently=False,
    )
    return token


class PasswordAuth(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['nickname', 'hash'],
            properties={
                'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                'hash': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description='OK'),
            400: openapi.Response(description='Bad request'),
            500: openapi.Response(description='Internal server error'),
        },
        operation_description='Authenticate Skatert Account by Password',
        tags=['Users']
    )
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode("utf-8"))
        except:
            errorResponse = JsonResponse({
                "error": {
                    "code": 400,
                    "description": "Некорректный формат данных"
                }                
            })
            errorResponse.status_code=400 # BadRequest
            return errorResponse

        nickname = data.get("nickname")     
        hash = data.get("hash")  
        if not nickname:
            errorResponse = JsonResponse({
                "error": {
                    "code": 223,
                    "description": "User is not specified"
                }                
            })
            errorResponse.status_code=400 # BadRequest
            return errorResponse
        if not hash:
            errorResponse = JsonResponse({
                "error": {
                    "code": 223,
                    "description": "Hash is not specified"
                }                
            })
            errorResponse.status_code=400 # BadRequest
            return errorResponse

        if not Account.objects.filter(user__nickname=nickname).exists():
            errorResponse = JsonResponse({
                "error": {
                    "code": 224,
                    "description": "No such user"
                }                
            })
            errorResponse.status_code=400 # BadRequest
            return errorResponse


        try:
            account = (
                Account.objects.filter(user__nickname=nickname)
                .filter(passwordhash=hash)
                .get()
            )
        except Exception as e :
            print(e)
            errorResponse = JsonResponse({
                "error": {
                    "code": 225,
                    "description": "Неверные учетные данные"
                }                
            })
            errorResponse.status_code=400 # BadRequest
            return errorResponse
        if account is None:
            errorResponse = JsonResponse({
                "error": {
                    "code": 225,
                    "description": "Неверные учетные данные"
                }                
            })
            errorResponse.status_code=400 # BadRequest
            return errorResponse

        if account.secondFactor:
            _email_request(account)
            response = JsonResponse({
                "error": {
                    "code": 0,
                    "description": "Successful step 1 of 2 factor"
                },    
                "token": "-"
            })
        else:
            AuthToken = create_email_token(account)
            response = JsonResponse({
                "error": {
                    "code": 201,
                    "description": "Successful authentication"
                },    
                "token": str(AuthToken.token)
            })
            response.set_cookie("token", str(AuthToken.token))
            response.set_cookie("nickname", nickname)

        return response


class EmailAuth(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['nickname', 'code'],
            properties={
                'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                'code': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description='OK'),
            400: openapi.Response(description='Bad request'),
            500: openapi.Response(description='Internal server error'),
        },
        operation_description='Authenicate Skatert Account by Email',
        tags=['Users']
    )
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode("utf-8"))
        except:
            errorResponse = JsonResponse({
                "error": {
                    "code": 400,
                    "description": "Некорректный формат данных"
                }                
            })
            errorResponse.status_code=400 # BadRequest
            return errorResponse

        nickname = data.get("nickname")
        if not nickname:
            return HttpResponseBadRequest("Не указан nickname")
        code = data.get("code")
        if not code:
            return HttpResponseBadRequest("Не указан email")

        # Поиск аккаунта
        account = Account.objects.filter(user__nickname=nickname).get()
        if not account:
            return HttpResponseBadRequest("Некорректные данные")

        # Поиск токена (тип - хеш-токен)
        AuthToken = AuthTokens.objects.filter(account=account).filter(type="hash").filter(token=code).get()
        if not AuthToken:
            return HttpResponseBadRequest("Некорректный код")
        # Проверка актуальности
        if datetime.datetime.now().timestamp() > AuthToken.expiration_date.timestamp():
            AuthToken.delete()
            return HttpResponseBadRequest("Токен не актуален. Попробуйте ещё раз.")

        # Смена типа токена - на email-token
        AuthToken = create_email_token(account, hash_token=AuthToken)

        response = JsonResponse({
            "token": str(AuthToken.token)
        })
        response.set_cookie("token", str(AuthToken.token))
        response.set_cookie("nickname", nickname)
        return response


class Logout(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['nickname', 'token'],
            properties={
                'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                'token': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description='OK'),
            400: openapi.Response(description='Bad request'),
            500: openapi.Response(description='Internal server error'),
        },
        operation_description='Logging Out Skatert Account',
        tags=['Users']
    )
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        response = HttpResponseRedirect('/login')
        response.delete_cookie('token')
        response.delete_cookie('nickname')
        return response


class Settings(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['nickname', 'token', 'lastfm', 'secondFactor'],
            properties={
                'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                'token': openapi.Schema(type=openapi.TYPE_STRING),
                'lastfm': openapi.Schema(type=openapi.TYPE_STRING),
                'secondFactor': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response(description='OK'),
            400: openapi.Response(description='Bad request'),
            500: openapi.Response(description='Internal server error'),
        },
        operation_description='Authenticate Skatert Account by Password',
        tags=['Users']
    )
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        try:
            data = json.loads(request.body.decode("utf-8"))
        except:
            return HttpResponseBadRequest("Некорректный формат данных")

        nickname = data.get("nickname")
        if not nickname:
            return HttpResponseBadRequest("Не указан никнейм")

        token = data.get('token')
        if not token:
            return HttpResponseBadRequest("Не указан токен")

        lastfmNickname = data.get('lastfm')
        if not lastfmNickname:
            return HttpResponseBadRequest("Не указан ник lastfm")

        secondFactor = data.get('secondFactor')
        if secondFactor is None:
            return HttpResponseBadRequest("Не указан способ аутентификации")

        if not check_token(nickname, token):
            return HttpResponseBadRequest("Неверный токен досутпа")

        user = User.objects.filter(nickname=nickname).get()
        if user is None:
            return HttpResponseBadRequest("Не найден пользователь")

        account = Account.objects.filter(user=user).get()
        if account is None:
            return HttpResponseBadRequest("Не найден аккаунт")

        user.lastfm = lastfmNickname
        user.save()
        account.secondFactor = secondFactor
        account.save()

        return HttpResponse()


def check_token(nickname, tokenVal):
    account = Account.objects.filter(user__nickname=nickname).get()
    if account is None:
        return False

    token = AuthTokens.objects.filter(account=account).filter(token=tokenVal).get()
    if token is None:
        return False

    if token.type != "email":
        return False

    if datetime.datetime.now().timestamp() > token.expiration_date.timestamp():
        token.delete()
        return False

    return True


@csrf_exempt
def create_hash_token(account):
    token = str(randint(100000, 999999))
    hashToken = AuthTokens(
        account=account,
        token=token,
        type="hash",
        expiration_date=datetime.datetime.now() + datetime.timedelta(minutes=15),
    )
    hashToken.save()
    return token


def create_email_token(account, hash_token=None):
    if hash_token is None:
        AuthToken = AuthTokens(account=account)
    else:
        AuthToken = hash_token

    AuthToken.token = hex(randint(100, 0xFFFFFFFF))
    AuthToken.type = "email"
    AuthToken.expiration_date = datetime.datetime.now() + datetime.timedelta(days=1)
    AuthToken.save()
    return AuthToken
