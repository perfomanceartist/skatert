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
from movies.models import Titles
import json

class GetAppliedGenres(APIView):
    @swagger_auto_schema(
        operation_summary="Get applied genres",
        operation_description="Retrieve the list of all applied music genres.",
        tags=["Movies"],
        responses={200: "The list of all applied music genres."},
    )
    def get(self, request, *args, **kwargs):
        try:
            genres = Titles.objects.values("titletype").distinct()
            print(genres)
            return JsonResponse(genres, safe=False)
        except (KeyError, RuntimeError, ValueError) as error:
            return HttpResponseServerError(error)
