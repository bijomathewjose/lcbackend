from django.urls import path
from .dashboard_views import HelloWorldAPI

urlpatterns = [
    path('hello/', HelloWorldAPI.as_view()),
]
