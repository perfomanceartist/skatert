from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render

from users.models import Account, User

from backend.auth import check_cookie



def skatert(request):
    if check_cookie(request) is False:
        return HttpResponseRedirect('/login')
    return render(request, "home/main_page.html")


def login(request):
    if check_cookie(request):
        return HttpResponseRedirect("/")
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

def subscriptions(request):
    if check_cookie(request) is False:
       return HttpResponseRedirect('/login')
    
    nickname = request.COOKIES.get("nickname")
    if nickname is None:
        return HttpResponseRedirect("/login")

    data = {
        "user": {
            "nickname": nickname,
        }
    }
    return render(request, "home/subscriptions_page.html", context=data)

def mypage(request):
    if check_cookie(request) is False:
        return HttpResponseRedirect('/login')

    nickname = request.COOKIES.get("nickname")
    if nickname is None:
        return HttpResponseRedirect("/login")

    data = {"user": {"nickname": nickname}}
    return render(request, "home/user_page.html", context=data)


def settings(request):
    if check_cookie(request) is False:
       return HttpResponseRedirect('/login')

    nickname = request.COOKIES.get("nickname")
    if nickname is None:
        return HttpResponseRedirect("/login")

    user = User.objects.filter(nickname=nickname).get()
    if user is None:
        return HttpResponseBadRequest()

    account = Account.objects.filter(user=user).get()
    if account is None:
        return HttpResponseBadRequest()

    data = {
        "user": {
            "nickname": nickname,
            "lastfmLogin": user.lastfm,
            "secondFactor": account.secondFactor,
        }
    }

    return render(request, "home/settings_page.html", context=data)
