from django.http import HttpResponse, HttpResponseBadRequest,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from backend.backend import getRecommendations, getUserByNickname, getTrackById, getTrackInformation, prepareUserInfo

# Create your views here.
def index(request):
    return HttpResponse("Страница пользователей")

# @csrf_exempt
# def lastfm_by_nick(request):
#     if request.method == "POST": 
#         return HttpResponse("user lastfm")
#     else:
#         return HttpResponseBadRequest("Некорректный метод запроса")
