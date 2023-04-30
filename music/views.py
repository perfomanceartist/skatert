from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from django.views import View

import backend.backend
from users.models import User
from backend.lastfm_integration import loadUserLastFM
from backend.backend import getRecommendations
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
        except RuntimeError as error:
            return HttpResponseServerError(error)


class GetUserGenres(View):
    def get(self, request, *args, **kwargs):
        nickname = request.GET.get('nickname')
        if nickname is None:
            return HttpResponseBadRequest('Skatert nickname should be specified for this type of request.')

        user = backend.backend.getUserByNickname(nickname)
        if user is None:
            return HttpResponseNotFound("User with nickname '" + nickname + "' is not found.")
        return JsonResponse(GenreList.fromUser(User.objects.get(nickname=nickname)).values)


class SetUserGenres(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            user = backend.backend.getUserByNickname(data["nickname"])
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

        track = backend.backend.getTrackById(trackId)
        if track is None:
            return HttpResponseNotFound('Specified track is not found.')

        answer = { "name": track.name,
                   "artist": track.artist,
                   "album": track.album,
                   "listens": track.lovers,
                   "recommendations": track.recommended }
        return JsonResponse(answer)


