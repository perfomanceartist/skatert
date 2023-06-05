from . import views
from django.urls import path



urlpatterns = [
    path('lastFM-integration/', views.MakeLastFmIntegration.as_view(), name="MakeLastFmIntegration"),
    path('getFavouriteGenres/', views.GetUserGenres.as_view(), name="GetUserGenres"),
    path('setFavouriteGenres/', views.SetUserGenres.as_view(), name="SetUserGenres"),
    path('getAppliedGenres/', views.GetAppliedGenres.as_view(), name="GetAppliedGenres"),
    path('getTrackInfo/', views.GetTrackById.as_view(), name="GetTrackInfo"),
    path('getUserFavouriteTracks/', views.GetUserFavouriteTracks.as_view(), name="GetUserFavouriteTracks"),
    path('getUsers/', views.GetUsers.as_view(), name="GetUsers"),
    path('getRecommendations/', views.GetRecommendations.as_view(), name="GetRecommendations"),
    path('clickLike/', views.ClickLike.as_view(), name="ClickLike"),
    path('clickDislike/', views.ClickDislike.as_view(), name="ClickDislike"),
]
