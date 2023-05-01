from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("mypage", views.lastfm_by_nick, name='lastfm_by_nick'),
]