from django.http import (
    JsonResponse,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseNotFound,
    HttpResponseForbidden,
    HttpResponseServerError,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from backend.auth import check_cookie
from users.models import User, Track
from backend.lastfm_integration import loadUserLastFM
from backend.backend import (
    getRecommendations,
    getUserByNickname,
    getTrackByInfo,
    getTrackById,
    getTrackInformation,
    prepareUserInfo,
    tryRemoveDislike,
    tryRemoveLike,
)
from backend.parameters import GenreNames, GenreList
import json


class MakeLastFmIntegration(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["nickname", "lastFmNickname"],
            properties={
                "nickname": openapi.Schema(type=openapi.TYPE_STRING),
                "lastFmNickname": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response(description="OK"),
            400: openapi.Response(description="Bad request"),
            500: openapi.Response(description="Internal server error"),
        },
        operation_description="Make integration with Last.fm",
        tags=["Music"],
    )
    def post(self, request, *args, **kwargs):
        try:
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        try:
            data = json.loads(request.body)
            print(data["nickname"], data["lastFmNickname"])
            result = loadUserLastFM(data["nickname"], data["lastFmNickname"])
            if result is False:
                return HttpResponseBadRequest("No such user")
            return JsonResponse(
                prepareUserInfo(
                    User.objects.get(
                        nickname=data["nickname"], lastfm=data["lastFmNickname"]
                    )
                )
            )
        except (KeyError, json.JSONDecodeError):
            return HttpResponseBadRequest("Failed to decode json data.")
        except (RuntimeError, ValueError) as error:
            return HttpResponseServerError(error)


class GetUserGenres(APIView):
    @swagger_auto_schema(
        operation_summary="Get user genres",
        operation_description="Get genres of a user by their nickname",
        manual_parameters=[
            openapi.Parameter(
                name="nickname",
                in_=openapi.IN_QUERY,
                description="The nickname of the user to get genres for",
                type=openapi.TYPE_STRING,
            )
        ],
        tags=["Music"],
        responses={
            200: openapi.Response(
                description="Genres successfully retrieved",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "genres": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(
                                type=openapi.TYPE_INTEGER
                            ),
                        )
                    },
                ),
            ),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            404: openapi.Response(
                description="User not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        nickname = request.GET.get("nickname")
        if nickname is None:
            return HttpResponseBadRequest(
                "Skatert nickname should be specified for this type of request."
            )

        user = getUserByNickname(nickname)
        if user is None:
            return HttpResponseNotFound(
                "User with nickname '" + nickname + "' is not found."
            )
        return JsonResponse(GenreList.fromUser(user).values)


class SetUserGenres(APIView):
    @swagger_auto_schema(
        operation_summary="Set user genres",
        operation_description="Set genres of a user by their nickname",
        tags=["Music"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "nickname": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The nickname of the user to set genres for",
                ),
                "genres": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(
                        type=openapi.TYPE_BOOLEAN,
                        description="The weight of the genre (true/false)",
                    ),
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Genres successfully set",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "nickname": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="The nickname of the user that genres were set for",
                        ),
                        "genres": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(
                                type=openapi.TYPE_BOOLEAN,
                                description="The weight of the genre (true/false)",
                            ),
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            404: openapi.Response(
                description="User not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        try:
            data = json.loads(request.body)

            user = getUserByNickname(data["nickname"])
            if user is None:
                return HttpResponseNotFound(
                    "User with nickname '" + data["nickname"] + "' is not found."
                )

            genres = GenreList.defaultList()
            for key in data["genres"]:
                genres.set(key, data["genres"][key])
            print(genres.values)
            genres.setToUser(user)

            return JsonResponse(prepareUserInfo(user))
        except (KeyError, json.JSONDecodeError):
            return HttpResponseBadRequest("Failed to decode json data.")
        except (RuntimeError, ValueError) as error:
            return HttpResponseServerError(error)


class GetAppliedGenres(APIView):
    @swagger_auto_schema(
        operation_summary="Get applied genres",
        operation_description="Retrieve the list of all applied music genres.",
        tags=["Music"],
        responses={200: "The list of all applied music genres."},
    )
    def get(self, request, *args, **kwargs):
        try:
            return JsonResponse(GenreNames, safe=False)
        except (KeyError, RuntimeError, ValueError) as error:
            return HttpResponseServerError(error)


class GetTrackById(APIView):
    @swagger_auto_schema(
        operation_summary="Get track by id",
        operation_description="Retrieve information about a track by its id.",
        tags=["Music"],
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                "Track id",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        try:
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        try:
            trackId = request.GET.get("id")
            if trackId is None:
                return HttpResponseBadRequest("Track id must be specified.")

            track = getTrackById(trackId)
            if track is None:
                return HttpResponseNotFound("Specified track is not found.")
            return JsonResponse(getTrackInformation(track))
        except (RuntimeError, ValueError, KeyError) as error:
            return HttpResponseServerError(error)


class GetUserFavouriteTracks(APIView):
    @swagger_auto_schema(
        operation_summary="Get a list of a user's favourite tracks",
        manual_parameters=[
            openapi.Parameter(
                name="nickname",
                in_=openapi.IN_QUERY,
                type="string",
                description="The nickname of the user whose favourite tracks are to be returned",
            )
        ],
        tags=["Music"],
        responses={
            200: openapi.Response(
                description="OK",
            ),
            400: openapi.Response(
                description="Bad Request",
                examples={"application/json": {"error": "Nickname must be specified."}},
            ),
            404: openapi.Response(
                description="Not Found",
                examples={
                    "application/json": {"error": "User 'nickname' is not found."}
                },
            ),
            500: openapi.Response(
                description="Internal Server Error",
                examples={"application/json": {"error": "Internal Server Error"}},
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        try:
            nickname = request.GET.get("nickname")
            if nickname is None:
                return HttpResponseBadRequest("Nickname must be specified.")

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
        tags=["Music"],
        responses={
            200: openapi.Response(
                description="List of all users",
                schema=openapi.Schema(
                    type=openapi.TYPE_STRING,
                ),
            ),
            500: "Internal server error",
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
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
            openapi.Parameter(
                "nickname",
                openapi.IN_QUERY,
                description="User nickname",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "amount",
                openapi.IN_QUERY,
                description="Amount of recommended tracks",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        tags=["Music"],
        responses={
            200: openapi.Response(
                description="Recommended tracks",
            ),
            400: "Bad Request",
            404: "Not Found",
            500: "Internal Server Error",
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        try:
            nickname = request.GET.get("nickname")
            if nickname is None:
                return HttpResponseBadRequest(
                    "Nickname should be specified for this type of requests."
                )

            amount = request.GET.get("amount")
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


def _prepareUserAndTrack(data: dict) -> tuple[User, Track]:
        nickname = data.get("nickname")
        song_name = data.get("song_name")
        song_artist = data.get("song_artist")

        if nickname is None or song_name is None or song_artist is None:
            raise KeyError(
                "Nickname, song name and song artist should be specified for this type of requests."
            )

        if (user := getUserByNickname(nickname)) is None:
            raise ValueError("User not found.")
        
        if (track := getTrackByInfo(song_name, song_artist)) is None:
            raise ValueError("Track not found.")

        return user, track


class ClickLike(APIView):
    @swagger_auto_schema(
        operation_summary="Like track",
        operation_description="Undislike and like a track",
        tags=["Music"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "nickname": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The nickname of the user to set genres for",
                ),
                "song_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Name of the song",
                ),
                "song_artist": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Name of the artist",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Like is set",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            404: openapi.Response(
                description="User not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        try:
            data = json.loads(request.body)
            user, track = _prepareUserAndTrack(data)
        except json.decoder.JSONDecodeError:
            return HttpResponseBadRequest("Incorrect json format.")
        except (KeyError, ValueError) as e:
            return HttpResponseNotFound("Data error: " + str(e))
        tryRemoveDislike(user, track)

        if track in user.favouriteTracks.all():
            user.favouriteTracks.remove(track)
        else:
            user.favouriteTracks.add(track)
        user.save()

        return HttpResponse(status=200)


class ClickDislike(APIView):
    @swagger_auto_schema(
        operation_summary="Dislike track",
        operation_description="Unlike and dislike a track",
        tags=["Music"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "nickname": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The nickname of the user to set genres for",
                ),
                "song_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Name of the song",
                ),
                "song_artist": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Name of the artist",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Dislike is set",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            400: openapi.Response(
                description="Bad request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            404: openapi.Response(
                description="User not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        try:
            data = json.loads(request.body)
            user, track = _prepareUserAndTrack(data)
        except json.decoder.JSONDecodeError:
            return HttpResponseBadRequest("Incorrect json format.")
        except (KeyError, ValueError) as e:
            return HttpResponseNotFound("Data error: " + str(e))

        tryRemoveLike(user, track)

        if track in user.unfavouriteTracks.all():
            user.unfavouriteTracks.remove(track)
        else:
            user.unfavouriteTracks.add(track)
        user.save()

        return HttpResponse(status=200)


class FindTrack(APIView):
    @swagger_auto_schema(
        operation_summary="Find track by its name",
        tags=["Music"],
        manual_parameters=[
            openapi.Parameter(
                "nickname",
                openapi.IN_QUERY,
                description="User nickname",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                name="track_name",
                in_=openapi.IN_QUERY,
                description="Name of track to find",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: openapi.Response(
                description="List of potential tracks",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_STRING
                    )
                ),
            ),
            500: "Internal server error",
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        
        
        try:
            answer = []
            nickname = request.GET.get("nickname")
            user = getUserByNickname(nickname)
            if user is None:
                return HttpResponseBadRequest(
                    "User must be specified for this type of request."
                )
            
            trackname = request.GET.get("track_name")
            if trackname is None or trackname == "":
                return HttpResponseBadRequest(
                    "Query string (track name) should be specified for this type of request."
                )

            tracks = Track.objects.filter(name__icontains=trackname)
            for track in tracks:
                search_track_info = getTrackInformation(track)
                if track in user.favouriteTracks.all():
                    search_track_info["in_favourite"] = True
                else:
                    search_track_info["in_favourite"] = False
                answer.append(search_track_info)
            

            return JsonResponse(answer, safe=False)
        except (RuntimeError, ValueError, KeyError) as error:
            return HttpResponseServerError(error)