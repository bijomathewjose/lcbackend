from uuid import uuid4
from rest_framework.views import APIView
from learningcircle.models import LearningCircle, CircleUserLink
import requests
from decouple import config
from utils.utils_views import CustomResponse, get_current_utc_time
from datetime import datetime
from .circle_serializer import LearningCircleSerializer


class CreateCircleView(APIView):
    def get_circle_code(self, org_code, org_id, ig_title, ig_id):
        circles_in_ig = LearningCircle.objects.filter(college_id=org_id, interest_group_id=ig_id)
        count = len(circles_in_ig)
        length_of_digit_count = len(str(count))
        text_length = (
            "".join(["0" for _ in range(3 - length_of_digit_count)]) if length_of_digit_count < 3 else ""
        ) + str(count)
        ig_sub = ig_title[0:3]
        return ig_sub.upper() + org_code + text_length

    def set_time_format(self, meet_time):
        if not meet_time:
            return CustomResponse(
                general_message="Meet time is required",
            ).get_failure_response()
        time_str = meet_time
        time_obj = datetime.strptime(time_str, "%I:%M %p")
        time_sql = time_obj.strftime("%H:%M:%S")
        return time_sql

    def validate(self, key, value):
        if not value or not len(value.strip()):
            return CustomResponse(general_message=f"{key} is required").get_failure_response()
        pass

    def post(self, request):
        for key, value in request.data.items():
            response = self.validate(key, value)
            if response:
                return response
        interest_group_id = request.data.get("interest_group_id")
        circle_name = request.data.get("circle_name")
        meet_place = request.data.get("meet_place")
        meet_time = request.data.get("meet_time")
        password = request.data.get("secret_key")
        user_id = request.headers.get("userId")
        if not user_id:
            return CustomResponse(
                general_message="User id is required",
            )
        meet_time = self.set_time_format(meet_time)
        print(user_id, interest_group_id)
        response = requests.get(
            config("FR_DOMAIN_NAME") + "/api/v1/lc/user-list", data={"userId": user_id, "igId": interest_group_id}
        )
        if not response:
            return CustomResponse(
                general_message=response.json()["message"],
            ).get_failure_response()

        circle_found = LearningCircle.objects.filter(name=circle_name).first() if circle_name == "" else None
        if circle_found and circle_found.name:
            return CustomResponse(
                general_message="Circle name already exists",
            ).get_failure_response()
        user_id, org_id, org_code, ig_title = response.json()["response"].values()
        circle_code = self.get_circle_code(org_code, org_id, ig_title, interest_group_id)
        new_circle = LearningCircle.objects.create(
            id=uuid4(),
            circle_code=circle_code,
            name=circle_name,
            password=password,
            interest_group_id=interest_group_id,
            college_id=org_id,
            lead_id=user_id,
            meet_place=meet_place,
            meet_time=meet_time,
            updated_by=user_id,
            updated_at=get_current_utc_time(),
            created_by=user_id,
            created_at=get_current_utc_time(),
        )
        circle_user = CircleUserLink.objects.create(
            id=uuid4(),
            circle=new_circle,
            user_id=user_id,
            accepted=True,
            accepted_at=get_current_utc_time(),
            created_at=get_current_utc_time(),
        )
        is_circle_created = ""
        if circle_user:
            is_circle_created = "User connected to circle successfully"

        return CustomResponse(
            general_message=f"Circle created successfully,{is_circle_created}",
        ).get_success_response()


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
