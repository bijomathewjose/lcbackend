from rest_framework.views import APIView
from utils.utils_views import CustomResponse


class HelloWorldAPI(APIView):

    def get(self, request):
        return CustomResponse(general_message='Hello World').get_success_response()
