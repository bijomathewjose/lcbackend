from rest_framework.serializers import ModelSerializer
from django.core import serializers
from .models import CircleUser, LearningCircle, CircleUserLink


class CircleUserSerializer(ModelSerializer):
    class Meta:
        model = CircleUser
        fields = "__all__"


class LearningCircleSerializer(ModelSerializer):
    class Meta:
        model = LearningCircle
        fields = "__all__"


class CircleUserLinkSerializer(ModelSerializer):
    class Meta:
        model = CircleUserLink
        fields = "__all__"
