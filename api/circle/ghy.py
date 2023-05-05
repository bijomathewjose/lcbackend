from uuid import uuid4
from rest_framework.views import APIView
from learningcircle.models import LearningCircle, CircleUserLink
import requests
from decouple import config
from utils.utils_views import CustomResponse, get_current_utc_time
from datetime import datetime
from .serializers import LearningCircleSerializer


class JoinCircleView(APIView):
    def post(self, request):
        user_id = request.headers.get("userId")
        circle_id = request.data.get("circle_id")
        circle_code = request.data.get("circle_code")
        password = request.data.get("secret_key")

        if not user_id:
            return CustomResponse(
                general_message="User id is required",
            ).get_failure_response()
        if not circle_id and not circle_code:
            return CustomResponse(
                general_message="Circle id or code is required",
            ).get_failure_response()
        circle_found = None
        if circle_code or circle_id:
            circle_found = LearningCircle.objects.filter(circle_code=circle_code).first()

        if circle_id:
            circle_found = LearningCircle.objects.filter(id=circle_id).first()

        if circle_found:
            if circle_found.password == password:
                circle_user = CircleUserLink.objects.create(
                    id=uuid4(),
                    circle=circle_found,
                    user_id=user_id,
                    accepted=True,
                    accepted_at=get_current_utc_time(),
                    created_at=get_current_utc_time(),
                )
                if circle_user:
                    return CustomResponse(
                        general_message="User connected to circle successfully",
                    ).get_success_response()
                else:
                    return CustomResponse(
                        general_message="User not connected to circle",
                    ).get_failure_response()
            elif not circle_found.password == password:
                return CustomResponse(general_message="Invalid password").get_failure_response()
            if not password:
                circle_user = CircleUserLink.objects.create(
                    id=uuid4(),
                    circle=circle_found,
                    user_id=user_id,
                    accepted=False,
                    accepted_at=None,
                    created_at=get_current_utc_time(),
                )


class RequestHandleView(APIView):
    def post(self, request):
        user_id = request.headers.get("userId")
        circle_id = request.data.get("circle_id")
        if not user_id:
            return CustomResponse(
                general_message="User id is required",
            ).get_failure_response()
        if not circle_id:
            return CustomResponse(
                general_message="Circle id is required",
            ).get_failure_response()

        accepted = request.data.get("accepted")
        circle_user = CircleUserLink.objects.filter(circle_id=circle_id).first()
        if circle_user:
            if accepted:
                circle_user.accepted = True
                circle_user.accepted_at = get_current_utc_time()
                circle_user.save()
                return CustomResponse(
                    general_message="User connected to circle successfully",
                ).get_success_response()
            else:
                circle_user.delete()
                return CustomResponse(
                    general_message="User removed from circle",
                )
        else:
            return CustomResponse(
                general_message="Circle not found",
            ).get_failure_response()
