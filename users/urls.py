from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("lastfm_nick", views.lastfm_by_nick),
    path("getUserLasfmInfo/", views.GetUserLastfmInfo.as_view()),
    path("setUserLasfmNickname", views.SetUserLastfmNickname.as_view()),
    path("subscribe", views.Subscribe.as_view())
]
