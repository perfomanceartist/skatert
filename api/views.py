import datetime
import json
from random import randint
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView


import music.lastfm_api
from users.models import AuthTokens, Account, User, MusicPreferences
import re


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
            required=['nickname', 'lastfm_nickname', 'email', 'hash'],
            properties={
                'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                'lastfm_nickname' : openapi.Schema(type=openapi.TYPE_STRING),
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
            return HttpResponseBadRequest("Некорректный формат данных")

        nickname = data.get("nickname")
        if User.objects.filter(nickname=nickname).exists():
            return HttpResponse(status=222)
        if not nickname:
            return HttpResponse(status=223)
        
        lastfm_nickname = data.get("lastfm_nickname")
        if not lastfm_nickname:
            return HttpResponse(status=223)

        email = data.get("email")
        if not email:
            return HttpResponse(status=223)
        if not _check_email(email):
            return HttpResponse(status=225)
        hash = data.get("hash")
        if not hash:
            return HttpResponse(status=223)

        user = User(nickname=nickname, lastfm = lastfm_nickname)
        user.save()
        account = Account(user=user, email=email, passwordhash=hash)
        account.save()

        music_prefs = MusicPreferences.objects.all()
        for music_pref in music_prefs:
            music_pref.usersBitmask += [False]
            music_pref.save()       

        return HttpResponse("Registered")
    



def _email_request(account):
    token = str(randint(100000, 999999))
    hashToken = AuthTokens(
        account=account,
        token=token,
        type="hash",
        expiration_date=datetime.datetime.now() + datetime.timedelta(minutes=15),
    )
    hashToken.save()

    send_mail(
        "Skatert. Код Подтверждения входа",  # subject
        f"Код подтверждения для входа в Skatert: {token}",  # message
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
        operation_description='Authenicate Skatert Account by Password',
        tags=['Users']
    )

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode("utf-8"))
        except:
            return HttpResponseBadRequest("Некорректный формат данных")

        nickname = data.get("nickname")
        if not Account.objects.filter(user__nickname=nickname).exists():
            return HttpResponse(status=224)
        if not nickname:
            return HttpResponse(status=223)
        hash = data.get("hash")
        if not hash:
            return HttpResponse(status=223)

        try:
            account = (
                Account.objects.filter(user__nickname=nickname)
                .filter(passwordhash=hash)
                .get()
            )
        except:
            return HttpResponseBadRequest("Неверные учетные данные")
        if account is None:
            return HttpResponseBadRequest("Неверные учетные данные")

        token = _email_request(account)
        return HttpResponse("Token: " + token)



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
            return HttpResponseBadRequest("Некорректный формат данных")

        nickname = data.get("nickname")
        if not nickname:
            return HttpResponseBadRequest("Не указан nickname")
        code = data.get("code")
        if not code:
            return HttpResponseBadRequest("Не указан email")

        account = Account.objects.filter(user__nickname=nickname).get()
        if not account:
            return HttpResponseBadRequest("Некорректные данные")

        token = AuthTokens.objects.filter(account=account).filter(token=code).get()
        if not token:
            return HttpResponseBadRequest("Некорректный код")
        if datetime.datetime.now().timestamp() > token.expiration_date.timestamp():
            token.delete()
            return HttpResponseBadRequest("Токен не актуален. Попробуйте ещё раз.")

        token.token = hex(randint(100, 0xFFFFFFFF))
        token.type = "email"
        token.expiration_date = datetime.datetime.now() + datetime.timedelta(days=1)
        token.save()
        response = JsonResponse({"token": str(token.token)})
        response.set_cookie("token", str(token.token))
        response.set_cookie("nickname", nickname)
        return response
        





@csrf_exempt
def user_logout(request):
    response = HttpResponseRedirect('/login')
    response.delete_cookie('token')
    response.delete_cookie('nickname')
    return response


@csrf_exempt
def music_integration(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except:
            return HttpResponseBadRequest("Некорректный формат данных")

        lastfm_nickname = data.get("lastfm")
        if not lastfm_nickname:
            return HttpResponse(status=223)

        nickname = request.COOKIES.get("nickname")
        if not nickname:
            return user_logout(request)

        try:
            music.lastfm_api.userGetInfo(lastfm_nickname)
        except RuntimeError as error:
            return HttpResponseBadRequest("Last fm user cannot be found: " + str(error))

        user = User.objects.get(nickname=nickname)
        user.lastfm = lastfm_nickname
        user.save()

        # tracks = lastfm.download_from_user(lastfm_nickname)
        # for track in tracks:
        #     t = user.favouriteTracks.add(track)
        #     if not t:  # Если t - не none
        #         track.rating += 1
        #         track.save()

        user.save()

        return HttpResponse(str(0)) #len(tracks)))
