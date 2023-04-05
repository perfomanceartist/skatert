from django.http import HttpResponse
from music.lastfm import LastFm


def index(request):
    lastfm = LastFm()
    res = lastfm.download_from_user("DreadlyMonk")
    return HttpResponse('ok')