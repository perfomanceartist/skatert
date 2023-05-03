import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render

from users.models import AuthTokens, Account


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


def check_cookie(request):
    nickname = request.COOKIES.get("nickname")
    token = request.COOKIES.get("token")
    if nickname is None or token is None:
        return False
    return check_token(nickname, token)


def skatert(request):
    if check_cookie(request) is False:
       return HttpResponseRedirect('/login')
    return render(request, "home/main_page.html")


def login(request):
    return render(request, "login/login_page.html")


def register(request):
    return render(request, "login/register_page.html")

def genres(request):
    nickname = request.COOKIES.get("reg_nickname")
    if nickname is None:
        return HttpResponseRedirect("/login")
    data = {"user": {"nickname": nickname}}
    return render(request, "login/genres_page.html", context=data)

def user(request, nickname):
    if check_cookie(request) is False:
        return HttpResponseRedirect("/login")
    data = {"user": {"nickname": nickname}}
    return render(request, "home/user_page.html", context=data)


def mypage(request):
    if check_cookie(request) is False:
       return HttpResponseRedirect('/login')

    nickname = request.COOKIES.get("nickname")
    if nickname is None:
        return HttpResponseRedirect("/login")

    data = {"user": {"nickname": nickname}}
    return render(request, "home/user_page.html", context=data)
