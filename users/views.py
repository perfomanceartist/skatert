import json

from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseNotFound, HttpResponseServerError,
                         JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from backend.backend import getUserByNickname
from music.lastfm_api import userGetInfo


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


class GetUserLastfmInfo(APIView):
    @swagger_auto_schema(
        operation_summary='Get user\'s lastFM information',
        manual_parameters=[
            openapi.Parameter(
                name='nickname',
                in_=openapi.IN_QUERY,
                type='string',
                description='lastFM_nickname of the user whose info is to be returned'
            )
        ],
        tags=['Users'],
        responses={
            200: openapi.Response(
                description='OK',
            ),
            400: openapi.Response(
                description='Bad Request',
                examples={
                    'application/json': {'error': 'Nickname must be specified.'}
                }
            ),
            404: openapi.Response(
                description='Not Found',
                examples={
                    'application/json': {'error': 'User \'nickname\' is not found.'}
                }
            ),
            500: openapi.Response(
                description='Internal Server Error',
                examples={
                    'application/json': {'error': 'Internal Server Error'}
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            nickname = request.GET.get('nickname')
            if nickname is None:
                return HttpResponseBadRequest('Nickname must be specified.')
            lastfm_user = userGetInfo(nickname)
            if lastfm_user.get("error", None) is not None:
                return HttpResponseNotFound("User '" + nickname + "' not found.")
            return JsonResponse(lastfm_user, safe=False)
        except (RuntimeError, ValueError, KeyError) as error:
            return HttpResponseServerError(error)


class SetUserLastfmNickname(APIView):
    @swagger_auto_schema(
        operation_summary='Set user lastfmnickname',
        tags=['Users'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nickname': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The nickname of the user to set LastfmNickname for'
                ),
                'lastfm_nickname': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='LastfmNickname to set'
                )
            },
        ),
        responses={
            200: openapi.Response(
                description='LastfmNickname successfully set',
            ),
            400: openapi.Response(
                description='Bad request',
            ),
            404: openapi.Response(
                description='User not found',
            )
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            user = getUserByNickname(data["nickname"])
            if user is None:
                return HttpResponseNotFound("User with nickname '" + data["nickname"] + "' is not found.")

            user.lastfm = data["lastfm_nickname"]
            user.save()
            return HttpResponse("")
        except (KeyError, json.JSONDecodeError):
            return HttpResponseBadRequest('Failed to decode json data.')
        except (RuntimeError, ValueError) as error:
            return HttpResponseServerError(error)