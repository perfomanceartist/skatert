from . import views
from django.urls import path



urlpatterns = [
    path('genres/', views.GetAppliedGenres.as_view(), name="MakeLastFmIntegration"),   
]
