from django.http import HttpResponse, HttpResponseBadRequest,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

import json

from backend.backend import getRecommendations, getUserByNickname, getTrackById, getTrackInformation, prepareUserInfo

# Create your views here.
def index(request):
    return HttpResponse("Страница пользователей")

@csrf_exempt
def lastfm_by_nick(request):
    if request.method == "POST": 
        data = json.loads(request.body)
        user = getUserByNickname(data["nickname"])
        return HttpResponse(str(user.lastfm))
    else:
        return HttpResponseBadRequest("Некорректный метод запроса")
