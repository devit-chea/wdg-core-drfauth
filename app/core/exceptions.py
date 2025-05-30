from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
    APIException,
)
from rest_framework.response import Response
from rest_framework import status


class BaseException(APIException):
    def __init__(
        self,
        message="An unexpected error occurred. Please try again later.",
        status_code=400,
    ):
        self.status_code = status_code
        detail = {"status_text": "error", "message": message}
        super().__init__(detail)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework (DRF).
    It standardizes API error responses.
    """

    # Get the standard DRF response
    response = exception_handler(exc, context)

    # Define default error response structure
    error_response = {
        "status_text": True,
        "error": {},  # Changed from "errors": {}
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "message": "An unexpected error occurred.",
    }

    # Handle specific DRF exceptions
    if isinstance(exc, ValidationError):
        error_response.update(
            {
                "error": exc.detail,  # Updated to "error"
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Validation failed.",
            }
        )
    elif isinstance(exc, NotAuthenticated):
        error_response.update(
            {
                "error": {
                    "detail": "Authentication credentials were not provided or invalid."
                },
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "message": "Authentication required.",
            }
        )
    elif isinstance(exc, PermissionDenied):
        error_response.update(
            {
                "error": {
                    "detail": "You do not have permission to perform this action."
                },
                "status_code": status.HTTP_403_FORBIDDEN,
                "message": "Permission denied.",
            }
        )
    elif isinstance(exc, NotFound):
        error_response.update(
            {
                "error": {"detail": "The requested resource was not found."},
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "Resource not found.",
            }
        )
    elif isinstance(exc, APIException):
        error_response.update(
            {
                "error": {"detail": str(exc.detail)},
                "status_code": exc.status_code,
                "message": "An API error occurred.",
            }
        )

    # If DRF has provided a response, use its status code
    if response is not None:
        error_response["status_code"] = response.status_code

    # Return a structured error response
    return Response(error_response, status=error_response["status_code"])
