from rest_framework.views import APIView
import requests
from decouple import config
from utils.utils_views import CustomResponse, get_current_utc_time
from learningcircle.models import LearningCircle, CircleUserLink
from datetime import datetime
from uuid import uuid4
from django.contrib.auth.hashers import make_password, check_password
import hmac


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
        ret_Val = None
        try:
            ret_Val = datetime.strptime(meet_time, "%I:%M %p").time()

        except:
            return CustomResponse(
                general_message="Invalid time format,Time format is HH:MM AM/PM"
            ).get_failure_response()
        return ret_Val

    def post(self, request):
        # get user id
        user_id = request.headers.get("userId")
        if not user_id:
            return CustomResponse(general_message="User id is required").get_failure_response()
        # get interest group id
        interest_group_id = request.data.get("ig_id")
        if not interest_group_id:
            return CustomResponse(general_message="Interest group id is required").get_failure_response()
        # get interest group title
        interest_group_title = request.data.get("ig_title")
        if not interest_group_title:
            return CustomResponse(general_message="Interest group title is required").get_failure_response()
        # get org id and org code
        response = requests.get(
            config("FR_DOMAIN_NAME") + "/api/v1/learning-circle/user-org/", headers={"userId": user_id}
        )
        if not response.status_code == 200:
            return CustomResponse(general_message=response.json()["message"]).get_failure_response()
        org_id = response.json()["response"]["org"]["id"]
        org_code = response.json()["response"]["org"]["code"]
        # get circle code
        circle_code = self.get_circle_code(org_code, org_id, interest_group_title, interest_group_id)
        circle = LearningCircle.objects.filter(circle_code=circle_code).first()

        if circle:
            return CustomResponse(general_message="Circle code already exists").get_failure_response()
        # get circle name
        circle_name = request.data.get("circle_name")
        if not circle_name:
            return CustomResponse(
                general_message="Circle name is required",
            ).get_failure_response()
        circle = LearningCircle.objects.filter(name=circle_name).first()
        if circle:
            return CustomResponse(general_message="Circle already exists").get_failure_response()
        # get meet place
        meet_place = request.data.get("meet_place")
        if not meet_place:
            return CustomResponse(general_message="Meet place is required").get_failure_response()
        # get meet time
        meet_time = self.set_time_format(request.data.get("meet_time"))
        try:
            if meet_time.status_code == 400:
                return meet_time
        except:
            pass

        # get secret key
        password = request.data.get("secret_key")
        if not password:
            return CustomResponse(
                general_message="Password is required",
            ).get_failure_response()
        else:
            password = hmac.new(
                key=config("SECRET_KEY").encode(), msg=password.encode(), digestmod="SHA256"
            ).hexdigest()
        circle = LearningCircle.objects.create(
            id=uuid4(),
            circle_code=circle_code,
            name=circle_name.lower(),
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
        user = None
        if circle:
            user = CircleUserLink.objects.create(
                id=uuid4(),
                circle_id=circle.id,
                user_id=user_id,
                accepted=True,
                accepted_at=get_current_utc_time(),
                created_at=get_current_utc_time(),
            )
        if user:
            return CustomResponse(general_message="Circle Created Successfully").get_success_response()
        else:
            return CustomResponse(general_message="Failed").get_failure_response()


class JoinCircleView(APIView):
    def post(self, request):
        user_id = request.headers.get("userId")
        org_id = None
        if user_id:
            response = requests.get(
                config("FR_DOMAIN_NAME") + "/api/v1/learning-circle/user-org/", headers={"userId": user_id}
            )
            if not response.status_code == 200:
                return CustomResponse(general_message=response.json()["message"]).get_failure_response()
            org_id = response.json()["response"]["org"]["id"]
        else:
            return CustomResponse(general_message="User id is required").get_failure_response()
        circle_code = request.data.get("circle_code")
        circle_id = request.data.get("circle_id")
        if not circle_code and not circle_id:
            return CustomResponse(general_message="Either Circle code or Circle id is required").get_failure_response()
        circle = None
        if circle_id:
            circle = LearningCircle.objects.filter(id=circle_id).first()
        elif circle_code:
            circle = LearningCircle.objects.filter(circle_code=circle_code).first()
        if not circle:
            return CustomResponse(general_message="Circle not found").get_failure_response()
        if circle.college_id != org_id:
            return CustomResponse(general_message="User not a student of the College").get_failure_response()
        circleUserLink = CircleUserLink.objects.filter(user_id=user_id, circle=circle).first()
        circleUsers = CircleUserLink.objects.filter(circle=circle)
        if circleUsers.count() >= 10:
            return CustomResponse(general_message="Circle is full").get_failure_response()

        if circleUserLink and circleUserLink.accepted:
            return CustomResponse(general_message="Already joined").get_failure_response()

        password = request.data.get("secret_key")
        user = None
        if password:
            password = hmac.new(
                key=config("SECRET_KEY").encode(), msg=password.encode(), digestmod="SHA256"
            ).hexdigest()
            isPasswordMatching = password == circle.password
            if not isPasswordMatching:
                return CustomResponse(general_message="Invalid password").get_failure_response()
            else:
                if circleUserLink:
                    circleUserLink.accepted = True
                    circleUserLink.accepted_at = get_current_utc_time()
                    try:
                        circleUserLink.save()
                        return CustomResponse(general_message="Joined Successfully").get_success_response()
                    except:
                        return CustomResponse(general_message="Failed").get_failure_response()
                else:
                    user = CircleUserLink.objects.create(
                        id=uuid4(),
                        circle=circle,
                        user_id=user_id,
                        accepted=True,
                        accepted_at=get_current_utc_time(),
                        created_at=get_current_utc_time(),
                    )
                if user:
                    return CustomResponse(general_message="Joined Successfully").get_success_response()
                else:
                    return CustomResponse(general_message="Failed").get_failure_response()
        else:
            if not circleUserLink:
                user = CircleUserLink.objects.create(
                    id=uuid4(),
                    circle=circle,
                    user_id=user_id,
                    accepted=False,
                    accepted_at=None,
                    created_at=get_current_utc_time(),
                )
            else:
                return CustomResponse(general_message="Already Requested").get_failure_response()
            if user:
                return CustomResponse(general_message="Requested Successfully").get_success_response()
            else:
                return CustomResponse(general_message="Failed").get_failure_response()


class circleRequestAcceptView(APIView):
    def post(self, request):
        circle_id = request.headers.get("circleId")
        user_id = request.headers.get("userId")
        if not circle_id:
            return CustomResponse(general_message="Circle id is required").get_failure_response()
        if not user_id:
            return CustomResponse(general_message="User id is required").get_failure_response()
        circleUserLink = CircleUserLink.objects.filter(circle_id=circle_id, user_id=user_id).first()
        if not circleUserLink:
            return CustomResponse(general_message="User not found for circle").get_failure_response()
        if circleUserLink.accepted:
            return CustomResponse(general_message="Already accepted").get_failure_response()
        circleUserLink.accepted = True
        circleUserLink.accepted_at = get_current_utc_time()
        try:
            circleUserLink.save()
            return CustomResponse(general_message="Accepted Successfully").get_success_response()
        except:
            return CustomResponse(general_message="Failed").get_failure_response()
