from django.db import IntegrityError
from rest_framework.exceptions import ValidationError, APIException


def extract_message(exc):
    try:
        if isinstance(exc, ValidationError):
            error_detail = exc.detail
            if isinstance(error_detail, list) and error_detail:
                return str(error_detail[0])
            if isinstance(error_detail, str):
                return error_detail
            if isinstance(error_detail, dict):
                if "non_field_errors" in error_detail:
                    non_field = error_detail["non_field_errors"]
                    if isinstance(non_field, list) and non_field:
                        return str(non_field[0])
                for key, value in error_detail.items():
                    if isinstance(value, list) and value:
                        if isinstance(value[0], dict):
                            first_error = value[0]
                            for sub_key, sub_value in first_error.items():
                                if isinstance(sub_value, list) and sub_value:
                                    return str(sub_value[0])
                        elif isinstance(value[0], str):
                            return value[0]
        elif isinstance(exc, IntegrityError):
            return "Database integrity error occurred."
        elif isinstance(exc, APIException):
            return exc.default_detail
        else:
            return str(exc)
    except Exception:
        return "An unexpected error occurred."
