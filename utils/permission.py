import datetime
from datetime import datetime

import jwt
from django.conf import settings
from django.http import HttpRequest
from rest_framework import authentication
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from .utils_views import get_current_utc_time
from lcbackend.settings import SECRET_KEY
from .exception import CustomException


def get_current_utc_time():
    return format_time(datetime.utcnow())


def format_time(date_time):
    formated_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    return datetime.strptime(formated_time, "%Y-%m-%d %H:%M:%S")


class CustomizePermission(BasePermission):
    """
    Custom permission class to authenticate user based on bearer token.

    Attributes:
        token_prefix (str): The prefix of the token in the header.
        secret_key (str): The secret key to verify the token signature.
    """

    token_prefix = "Bearer"
    secret_key = SECRET_KEY

    def authenticate(self, request):
        """
        Authenticates the user based on the bearer token in the header.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            tuple: A tuple of (user, token_payload) if authentication is successful.

        Raises:
            CustomException: If authentication fails.
        """
        try:
            auth_header = get_authorization_header(request).decode("utf-8")
            if not auth_header or not auth_header.startswith(self.token_prefix):
                raise CustomException("Invalid token header")

            token = auth_header[len(self.token_prefix) :].strip()
            if not token:
                raise CustomException("Empty Token")

            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"], verify=True)

            user_id = payload.get("id")
            expiry = datetime.strptime(payload.get("expiry"), "%Y-%m-%d %H:%M:%S")

            if not user_id or expiry < get_current_utc_time():
                raise CustomException("Token Expired or Invalid")

            return None, payload
        except jwt.exceptions.InvalidSignatureError as e:
            raise CustomException(
                {
                    "hasError": True,
                    "message": {"general": [str(e)]},
                    "statusCode": 1000,
                }
            )
        except jwt.exceptions.DecodeError as e:
            raise CustomException(
                {
                    "hasError": True,
                    "message": {"general": [str(e)]},
                    "statusCode": 1000,
                }
            )
        except AuthenticationFailed as e:
            raise CustomException(str(e))
        except Exception as e:
            raise CustomException(
                {
                    "hasError": True,
                    "message": {"general": [str(e)]},
                    "statusCode": 1000,
                }
            )

    def authenticate_header(self, request):
        """
        Returns a string value for the WWW-Authenticate header.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            str: The value for the WWW-Authenticate header.
        """
        return self.token_prefix + ' realm="api"'


class JWTUtils:
    @staticmethod
    def fetch_user_id(request):
        token = authentication.get_authorization_header(request).decode("utf-8").split()
        payload = jwt.decode(token[1], settings.SECRET_KEY, algorithms=["HS256"], verify=True)
        id = payload.get("id")
        if id is None:
            raise Exception("The corresponding JWT token does not contain the 'id' key")
        return id
