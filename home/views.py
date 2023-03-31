import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from users.models import AuthTokens, UserAuth


def check_token(nickname, tokenVal):
    user = UserAuth.objects.filter(nickname=nickname).get()
    if user is None:
        return False

    token = AuthTokens.objects.filter(user=user).filter(token=tokenVal).get()
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
        nickname = request.COOKIES["nickname"]
    except:
        return False

    try:
        token = request.COOKIES["token"]
    except:
        return False
    return check_token(nickname, token)


def skatert(request):
    # if check_cookie(request) is False:
    #    return HttpResponseRedirect('/login')
    return render(request, "main_page.html")


def login(request):
    return render(request, "login_page.html")


def register(request):
    return render(request, "register_page.html")


def user(request, nickname):
    if check_cookie(request) is False:
        return HttpResponseRedirect("/login")
    data = {"user": {"nickname": nickname}}
    return render(request, "user_page.html", context=data)


def mypage(request):
    # if check_cookie(request) is False:
    #    return HttpResponseRedirect('/login')

    try:
        nickname = request.COOKIES["nickname"]
    except:
        return HttpResponseRedirect("/login")

    data = {"user": {"nickname": nickname}}
    return render(request, "user_page.html", context=data)
