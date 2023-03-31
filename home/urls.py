from django.urls import path, re_path

from . import views

urlpatterns = [    
    path('user/<slug:nickname>', views.user, name='user'),
    path('mypage', views.mypage, name='mypage'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('', views.index, name='index'),
]
