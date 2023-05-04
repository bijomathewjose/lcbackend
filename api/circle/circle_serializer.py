from rest_framework.serializers import ModelSerializer
from learningcircle.models import LearningCircle


class LearningCircleSerializer(ModelSerializer):
    class Meta:
        model = LearningCircle
        fields = "__all__"
