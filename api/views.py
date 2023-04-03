import datetime
import json
from random import randint
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from users.models import AuthTokens, UserAuth
import re


def index(request):
    return HttpResponse("API")


def _check_email(email: str):
    regex = re.compile(r"([a-zA-Z0-9]+[._-])*[a-zA-Z0-9]+@[a-zA-Z0-9]+(\.[A-Z|a-z]{2,})+")
    if re.fullmatch(regex, email):
        return True
    return False


@csrf_exempt
def register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            return HttpResponseBadRequest("Некорректный формат данных")

        nickname = data.get("nickname")
        if UserAuth.objects.filter(nickname=nickname).exists():
            return HttpResponse(status=222)
        if not nickname:
            return HttpResponse(status=223)

        email = data.get("email")
        if not email:
            return HttpResponse(status=223)
        if not _check_email(email):
            return HttpResponse(status=225)

        hash = data.get("hash")
        if not hash:
            return HttpResponse(status=223)

        user = UserAuth(nickname=nickname, email=email, passwordhash=hash)
        user.save()
        return HttpResponse("Registered")
    else:
        return HttpResponseBadRequest("Некорректный метод запроса")


def _email_request(user):
    token = str(randint(100000, 999999))
    hashToken = AuthTokens(
        user=user,
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
            user.email,
        ],
        fail_silently=False,
    )
    return token


@csrf_exempt
def password_auth(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except:
            return HttpResponseBadRequest("Некорректный формат данных")

        nickname = data.get("nickname")
        if not UserAuth.objects.filter(nickname=nickname).exists():
            return HttpResponse(status=224)
        if not nickname:
            return HttpResponse(status=223)
        hash = data.get("hash")
        if not hash:
            return HttpResponse(status=223)

        try:
            user = (
                UserAuth.objects.filter(nickname=nickname)
                .filter(passwordhash=hash)
                .get()
            )
        except:
            return HttpResponseBadRequest("Неверные учетные данные")
        if user is None:
            return HttpResponseBadRequest("Неверные учетные данные")

        token = _email_request(user)
        return HttpResponse("Token: " + token)
    else:
        return HttpResponseBadRequest("Некорректный метод запроса")


@csrf_exempt
def email_auth(request):
    if request.method == "POST":
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

        user = UserAuth.objects.filter(nickname=nickname).get()
        if not user:
            return HttpResponseBadRequest("Некорректные данные")

        token = AuthTokens.objects.filter(user=user).filter(token=code).get()
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
    else:
        return HttpResponseBadRequest("Некорректный метод запроса")


@csrf_exempt
def user_logout(request):
    response = HttpResponseRedirect('/login')
    response.delete_cookie('token')
    response.delete_cookie('nickname')
    return response