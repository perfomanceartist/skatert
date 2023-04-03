from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login_pass", views.password_auth),
    path("login_email", views.email_auth),
    path("register", views.register),
    path("logout", views.user_logout)
]
