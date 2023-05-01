from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, \
    HttpResponseServerError
from django.views import View

import backend.display
from users.models import User
from backend.lastfm_integration import loadUserLastFM
from backend.backend import getRecommendations, getUserByNickname, getTrackById, getTrackInformation
from backend.parameters import GenreNames, GenreList
import json


def index(request):
    pass


class MakeLastFmIntegration(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            loadUserLastFM(data["nickname"], data["lastFmNickname"])
            return HttpResponse('LastFM integration completed')
        except (KeyError, json.JSONDecodeError):
            return HttpResponseBadRequest('Failed to decode json data.')
        except (RuntimeError, ValueError) as error:
            return HttpResponseServerError(error)


class GetUserGenres(View):
    def get(self, request, *args, **kwargs):
        backend.display.showMusicPreferences()
        nickname = request.GET.get('nickname')
        if nickname is None:
            return HttpResponseBadRequest('Skatert nickname should be specified for this type of request.')

        user = getUserByNickname(nickname)
        if user is None:
            return HttpResponseNotFound("User with nickname '" + nickname + "' is not found.")

        print("Nickname:", nickname, "id:", int(user.id))
        return JsonResponse(GenreList.fromUser(user).values)


class SetUserGenres(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            user = getUserByNickname(data["nickname"])
            if user is None:
                return HttpResponseNotFound("User with nickname '" + data["nickname"] + "' is not found.")

            # specifiedValues = json.loads(json_string)
            # values = {name: False for name in genreNames}
            # for key in values:
            #     if key in specifiedValues:
            #         values[key] = specifiedValues[key]
            #
            # setUserGenres(user, (values[name] for name in genreNames))
        except (KeyError, json.JSONDecodeError):
            return HttpResponseBadRequest('Failed to decode json data.')


class GetAppliedGenres(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse(GenreNames, safe=False)


class GetTrackById(View):
    def get(self, request, *args, **kwargs):
        trackId = request.GET.get('id')
        if trackId is None:
            return HttpResponseBadRequest('Track id must be specified.')

        track = getTrackById(trackId)
        if track is None:
            return HttpResponseNotFound('Specified track is not found.')
        return JsonResponse(getTrackInformation(track))


class GetUserFavouriteTracks(View):
    def get(self, request, *args, **kwargs):
        nickname = request.GET.get('nickname')
        if nickname is None:
            return HttpResponseBadRequest('Nickname must be specified.')

        user = getUserByNickname(nickname)
        if user is None:
            return HttpResponseNotFound("User '" + nickname + "' is not found.")

        answer = []
        for track in user.favouriteTracks.all():
            answer.append(getTrackInformation(track))
        return JsonResponse(answer, safe=False)


class GetUsers(View):
    def get(self, request, *args, **kwargs):
        answer = []
        for user in User.objects.all():
            answer.append({"nickname": user.nickname,
                           "lastFmNickname": user.lastfm,
                           "favouriteTracksAmount": len(user.favouriteTracks.all()),
                           "genres": dict(GenreList.fromUser(user).values)})
        return JsonResponse(answer, safe=False)


class GetRecommendations(View):
    def get(self, request, *args, **kwargs):
        nickname = request.GET.get('nickname')
        if nickname is None:
            return HttpResponseBadRequest("Nickname should be specified for this type of requests.")

        amount = request.GET.get('amount')
        if amount is None or int(amount) < 1:
            return HttpResponseBadRequest("Incorrect amount of records.")

        user = getUserByNickname(nickname)
        if user is None:
            return HttpResponseNotFound("User '" + nickname + "' is not found.")

        answer = []
        for track in getRecommendations(user, amount):
            answer.append(getTrackInformation(track))
        return JsonResponse(answer, safe=False)



