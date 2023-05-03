from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("lastfm", views.lastfm_by_nick)
]