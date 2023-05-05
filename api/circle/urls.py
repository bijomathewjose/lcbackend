from django.urls import include, path
from .circle_views import CreateCircleView

urlpatterns = [
    path("create/", CreateCircleView.as_view()),
    # path("join/", JoinCircleView.as_view()),
    # path("request/", RequestHandleView.as_view()),
]
