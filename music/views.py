from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, \
    HttpResponseServerError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from users.models import User
from backend.lastfm_integration import loadUserLastFM
from backend.backend import getRecommendations, getUserByNickname, getTrackById, getTrackInformation, prepareUserInfo
from backend.parameters import GenreNames, GenreList
import json


class MakeLastFmIntegration(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['nickname', 'lastFmNickname'],
            properties={
                'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                'lastFmNickname': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(description='OK'),
            400: openapi.Response(description='Bad request'),
            500: openapi.Response(description='Internal server error'),
        },
        operation_description='Make integration with Last.fm',
        tags=['Music']
    )
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            loadUserLastFM(data["nickname"], data["lastFmNickname"])
            return JsonResponse(prepareUserInfo(User.objects.get(nickname=data['nickname'], lastfm=data['lastFmNickname'])))
        except (KeyError, json.JSONDecodeError):
            return HttpResponseBadRequest('Failed to decode json data.')
        except (RuntimeError, ValueError) as error:
            return HttpResponseServerError(error)


class GetUserGenres(APIView):
    @swagger_auto_schema(
        operation_summary='Get user genres',
        operation_description='Get genres of a user by their nickname',
        manual_parameters=[
            openapi.Parameter(
                name='nickname',
                in_=openapi.IN_QUERY,
                description='The nickname of the user to get genres for',
                type=openapi.TYPE_STRING
            )
        ],
        tags=['Music'],
        responses={
            200: openapi.Response(
                description='Genres successfully retrieved',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'genres': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(
                                type=openapi.TYPE_INTEGER
                            )
                        )
                    }
                )
            ),
            400: openapi.Response(
                description='Bad request',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING
                        )
                    }
                )
            ),
            404: openapi.Response(
                description='User not found',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING
                        )
                    }
                )
            )
        }
    )
    def get(self, request, *args, **kwargs):
        nickname = request.GET.get('nickname')
        if nickname is None:
            return HttpResponseBadRequest('Skatert nickname should be specified for this type of request.')

        user = getUserByNickname(nickname)
        if user is None:
            return HttpResponseNotFound("User with nickname '" + nickname + "' is not found.")
        return JsonResponse(GenreList.fromUser(user).values)


class SetUserGenres(APIView):
    @swagger_auto_schema(
        operation_summary='Set user genres',
        operation_description='Set genres of a user by their nickname',
        tags=['Music'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nickname': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The nickname of the user to set genres for'
                ),
                'genres': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description='The weight of the genre (true/false)'
                    )
                )
            },
        ),
        responses={
            200: openapi.Response(
                description='Genres successfully set',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'nickname': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='The nickname of the user that genres were set for'
                        ),
                        'genres': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(
                                type=openapi.TYPE_BOOLEAN,
                                description='The weight of the genre (true/false)'
                            )
                        )
                    }
                )
            ),
            400: openapi.Response(
                description='Bad request',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING
                        )
                    }
                )
            ),
            404: openapi.Response(
                description='User not found',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING
                        )
                    }
                )
            )
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            user = getUserByNickname(data["nickname"])
            if user is None:
                return HttpResponseNotFound("User with nickname '" + data["nickname"] + "' is not found.")

            genres = GenreList.defaultList()
            for key in data["genres"]:
                genres.set(key, data["genres"][key])
            genres.setToUser(user)

            return JsonResponse(prepareUserInfo(user))
        except (KeyError, json.JSONDecodeError):
            return HttpResponseBadRequest('Failed to decode json data.')
        except (RuntimeError, ValueError) as error:
            return HttpResponseServerError(error)


class GetAppliedGenres(APIView):
    @swagger_auto_schema(
        operation_summary="Get applied genres",
        operation_description="Retrieve the list of all applied music genres.",
        tags=['Music'],
        responses={
            200: "The list of all applied music genres."
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            return JsonResponse(GenreNames, safe=False)
        except (KeyError, RuntimeError, ValueError) as error:
            return HttpResponseServerError(error)


class GetTrackById(APIView):
    @swagger_auto_schema(
        operation_summary='Get track by id',
        operation_description='Retrieve information about a track by its id.',
        tags=['Music'],
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, 'Track id', type=openapi.TYPE_STRING, required=True)]
    )
    def get(self, request, *args, **kwargs):
        try:
            trackId = request.GET.get('id')
            if trackId is None:
                return HttpResponseBadRequest('Track id must be specified.')

            track = getTrackById(trackId)
            if track is None:
                return HttpResponseNotFound('Specified track is not found.')
            return JsonResponse(getTrackInformation(track))
        except (RuntimeError, ValueError, KeyError) as error:
            return HttpResponseServerError(error)


class GetUserFavouriteTracks(APIView):
    @swagger_auto_schema(
        operation_summary='Get a list of a user\'s favourite tracks',
        manual_parameters=[
            openapi.Parameter(
                name='nickname',
                in_=openapi.IN_QUERY,
                type='string',
                description='The nickname of the user whose favourite tracks are to be returned'
            )
        ],
        tags=['Music'],
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

            user = getUserByNickname(nickname)
            if user is None:
                return HttpResponseNotFound("User '" + nickname + "' is not found.")

            answer = []
            for track in user.favouriteTracks.all():
                answer.append(getTrackInformation(track))
            return JsonResponse(answer, safe=False)
        except (RuntimeError, ValueError, KeyError) as error:
            return HttpResponseServerError(error)


class GetUsers(APIView):
    @swagger_auto_schema(
        operation_summary="Get a list of all users",
        operation_description="Retrieve a list of all users with their details",
        tags=['Music'],
        responses={
            200: openapi.Response(
                description="List of all users",
                schema=openapi.Schema(
                    type=openapi.TYPE_STRING,
                ),
            ),
            500: "Internal server error",
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            answer = []
            for user in User.objects.all():
                answer.append(prepareUserInfo(user))
            return JsonResponse(answer, safe=False)
        except (RuntimeError, ValueError, KeyError) as error:
            return HttpResponseServerError(error)


class GetRecommendations(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('nickname', openapi.IN_QUERY, description="User nickname", type=openapi.TYPE_STRING),
            openapi.Parameter('amount', openapi.IN_QUERY, description="Amount of recommended tracks",
                              type=openapi.TYPE_INTEGER),
        ],
        tags=['Music'],
        responses={
            200: openapi.Response(description="Recommended tracks",),
            400: "Bad Request",
            404: "Not Found",
            500: "Internal Server Error"
        }
    )
    def get(self, request, *args, **kwargs):
        try:
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
            for track in getRecommendations(user, int(amount)):
                answer.append(getTrackInformation(track))
            return JsonResponse(answer, safe=False)
        except (RuntimeError, ValueError, KeyError, TypeError) as error:
            return HttpResponseServerError(error)



