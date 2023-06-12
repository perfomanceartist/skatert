from django.urls import path, re_path

from . import views

urlpatterns = [
    path('user/<slug:nickname>', views.user, name='user'),
    path('mypage', views.mypage, name='mypage'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('genres', views.genres, name='genres'),
    path('subscriptions', views.subscriptions, name='subscriptions'),
    path('settings', views.settings, name='settings'),
    path('', views.skatert, name='skatert'),
]
