from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/step1', views.password_auth),
    path('login/step2', views.email_auth),
    path('register/step1', views.register),
]