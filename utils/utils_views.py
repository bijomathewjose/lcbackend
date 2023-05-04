from rest_framework import status
from rest_framework.response import Response
from datetime import datetime


# Create your views here.
class CustomResponse:
    def __init__(self, message={}, general_message=[], response={}):
        if not isinstance(general_message, list):
            general_message = [general_message]

        self.message = {"general": general_message}
        self.message.update(message)
        self.response = response

    def get_success_response(self):
        return Response(
            data={"hasError": False, "statusCode": 200, "message": self.message, "response": self.response},
            status=status.HTTP_200_OK,
        )

    def get_failure_response(self, status_code=400, http_status_code=status.HTTP_400_BAD_REQUEST):
        return Response(
            data={"hasError": True, "statusCode": status_code, "message": self.message, "response": self.response},
            status=http_status_code,
        )


def get_current_utc_time():
    return format_time(datetime.utcnow())


def format_time(date_time):
    formated_time = date_time.strftime("%d/%m/%Y %H:%M:%S")
    return datetime.strptime(formated_time, "%d/%m/%Y %H:%M:%S")
