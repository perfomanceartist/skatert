import json

from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseNotFound, HttpResponseServerError,
                         HttpResponseForbidden,
                         JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from backend.backend import getUserByNickname
from music.lastfm_api import userGetInfo

from backend.auth import check_cookie
from users.models import User

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
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        try:
            nickname = request.COOKIES.get("nickname")
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
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        try:
            data = json.loads(request.body)
            nickname = request.COOKIES.get("nickname")
            user = getUserByNickname(nickname)
            if user is None:
                return HttpResponseNotFound("User with nickname '" + nickname + "' is not found.")

            user.lastfm = data["lastfm_nickname"]
            user.save()
            return HttpResponse("")
        except (KeyError, json.JSONDecodeError):
            return HttpResponseBadRequest('Failed to decode json data.')
        except (RuntimeError, ValueError) as error:
            return HttpResponseServerError(error)



class Subscribe(APIView):
    @swagger_auto_schema(
        operation_summary='Subscribe to user',
        tags=['Users'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'target_nickname': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The nickname of the target user'
                ),
                'subscribed': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description='if true, trying to subscribe, if false, trying to unsubscribe'
                )
            },
        ),
        responses={
            200: openapi.Response(
                description='Subscribed',
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
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        try:
            nickname = request.COOKIES.get("nickname")            
            data = json.loads(request.body)
            data["nickname"] = nickname

            user = getUserByNickname(data["nickname"])
            if user is None:
                return HttpResponseNotFound("User with nickname '" + data["nickname"] + "' is not found.")

            target = getUserByNickname(data["target_nickname"])
            if target is None:
                return HttpResponseNotFound("User with nickname '" + data["target_nickname"] + "' is not found.")
              
            action = data["subscribed"]
            if action == True:
                if target.id in user.subscriptions:
                    return HttpResponseBadRequest("Already subscribed to target")
                user.subscriptions.append(target.id)
            else:
                if not target.id in user.subscriptions:
                    return HttpResponseBadRequest("User was not subscribed to target")
                user.subscriptions.remove(target.id)
            user.save()
            return HttpResponse("")
        except (KeyError, json.JSONDecodeError):
            return HttpResponseBadRequest('Failed to decode json data.')
        except (RuntimeError, ValueError) as error:
            return HttpResponseServerError(error)
        



class GetUserSubscriptions(APIView):
    @swagger_auto_schema(
        operation_summary='Get user\'s subscriptions list',
        tags=['Users'],
        responses={
            200: openapi.Response(
                description='OK',
		examples={
                    'application/json': ['user1', 'user2']
                }
            ),
            400: openapi.Response(
                description='Bad Request',
                examples={
                    'application/json': {'error': 'Nickname must be specified.'}
                }
            ),
            403: openapi.Response(
                description='Not Authorised',
                examples={
                    'application/json': {'error': 'Bad cookie.'}
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
            if not check_cookie(request):
                return HttpResponseForbidden("Bad cookie")
        except Exception as error:
            print(error)
            return HttpResponseForbidden("Bad cookie")
        try:
            nickname = request.COOKIES.get("nickname")
            if nickname is None:
                return HttpResponseBadRequest('Nickname must be specified.')
            
            user = getUserByNickname(nickname)
            if user is None:
                return HttpResponseNotFound("User with nickname '" + nickname + "' is not found.")
            subs = []
            for id in user.subscriptions:
                try:
                    sub = User.objects.filter(id=id).get()
                    if sub is None:
                        return HttpResponseServerError("В списке пользователей плохой айди")
                except Exception as e:
                    return HttpResponseServerError(e)
                subs.append(sub.nickname)
            

            return JsonResponse(subs, safe=False)
        except (RuntimeError, ValueError, KeyError) as error:
            return HttpResponseServerError(error)