from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/step1', views.email_auth),
    path('register/step1', views.register),
    path ('login/step2', views.password_auth)
]