from django.urls import include, path
from .circle_views import CreateCircleView, JoinCircleView, circleRequestAcceptView

urlpatterns = [
    path("create/", CreateCircleView.as_view()),
    path("join/", JoinCircleView.as_view()),
    path("accept/", circleRequestAcceptView.as_view()),
]
