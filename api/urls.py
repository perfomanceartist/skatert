from django.urls import path,re_path
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Skatert API",
      default_version='v0.1',
      description="Сервис рекомендаций",
      contact=openapi.Contact(email="skatertTeam@yandex.ru"),
      license=openapi.License(name="CopyLeft"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)



urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("", views.index, name="index"),
    path("login_pass", views.PasswordAuth.as_view()),
    path("login_email", views.EmailAuth.as_view()),
    path("register", views.Register.as_view()),
    path("logout", views.Logout.as_view()),
    path("settings", views.Settings.as_view()),
    path("integrate", views.music_integration)
]
