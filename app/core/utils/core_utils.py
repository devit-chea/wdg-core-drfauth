import re
from decimal import Decimal
from datetime import datetime
from rest_framework import serializers
from apps.core.constants import ExcludeMetaField
from rest_framework.validators import UniqueValidator

from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

date_format = "%Y-%m-%d"


def get_relationship_field(model):
    result = []
    fields = model._meta.get_fields()
    for field in fields:
        if field.is_relation and hasattr(field, "null") and not field.null:
            result.append(field)
    return result


def get_model_fields_only(model):
    fields = model._meta.get_fields()
    result = []
    for field in fields:
        field_name = field.name
        if not field.is_relation:
            result.append(field_name)
    return result


def shorten_name(full_name: str, uppercase: bool = True) -> str:
    # Split by spaces and hyphens, keeping only meaningful parts
    parts = re.split(r"[\s-]+", full_name.strip())

    # Extract first alphabetic letter from each part
    initials = [next((ch for ch in p if ch.isalpha()), "") for p in parts if p]

    # Limit to max 4 characters
    result = "".join(initials[:4])

    return result.upper() if uppercase else result.lower()


def is_new_year(get_date: bool = False):
    dt = datetime.today()
    today = dt.strftime(date_format)
    yearly = datetime(dt.year, 1, 1).strftime(date_format)
    if today == yearly:
        return yearly if get_date else True
    return False


def is_new_month(get_date: bool = False):
    dt = datetime.today()
    today = dt.strftime(date_format)
    monthly = datetime(dt.year, dt.month, 1).strftime(date_format)
    if today == monthly:
        return monthly if get_date else True
    return False


def replace_multi_strings(text: str, replace_obj: dict):
    if not text or not replace_obj:
        return ""
    for i, j in replace_obj.items():
        text = text.replace(i, j)
    return str(text)


def get_date_format(date_time: datetime = None, str_format: str = None):
    if not date_time:
        date_time = datetime.now()
    if str_format:
        return date_time.strftime(str_format)
    return date_time.strftime("%Y-%m-%d")


def get_model_fields_only(model):
    fields = model._meta.get_fields()
    result = []
    for field in fields:
        field_name = field.name
        if not field.is_relation:
            result.append(field_name)
    return result


def get_model_fields(model, is_show_related=False):
    # get all field from model
    fields = model._meta.get_fields()
    result = []
    for f in fields:
        field = f.name
        if not is_show_related and not f.is_relation:
            result.append(field)
        else:
            if (
                hasattr(f, "get_internal_type")
                and not f.get_internal_type() == "ManyToManyField"
            ):
                result.append(field)
    return result


def separate_value(param):
    field_value = ""
    expression = ""
    default_operator = [
        "like",
        "not_like",
        "equal",
        "not_equal",
        "is_set",
        "is_not_set",
        "true",
        "false",
        "lte",
        "gte",
        "gt",
        "lt",
        "in",
        "not_in",
    ]

    extra_operator = {
        ">": "gt",
        ">=": "gte",
        "<": "lt",
        "<=": "lte",
    }

    if param:
        if isinstance(param, str) and "," in param:
            string = param.split(",", 1)
            expression = string[0].strip()
            field_value = string[1].strip()

        elif param == "is_set" or param == "is_not_set":
            expression = param
        elif param == "true":
            field_value = True
        elif param == "false":
            field_value = False
        else:
            field_value = param

        if expression in extra_operator:
            expression = extra_operator.get(expression, "")

        if expression not in default_operator:
            expression = ""
    return field_value, expression


def get_relationship_field(model):
    result = []
    fields = model._meta.get_fields()
    for field in fields:
        if field.is_relation and hasattr(field, "null") and not field.null:
            result.append(field)
    return result


def convert_internal_value_to_dict(internal_value):
    if isinstance(internal_value, dict):
        return {
            k: convert_internal_value_to_dict(v)
            for k, v in internal_value.items()
            if not k.startswith("_") and k not in ExcludeMetaField.get_exclude_field()
        }
    elif isinstance(internal_value, list) or isinstance(internal_value, tuple):
        return [convert_internal_value_to_dict(v) for v in internal_value]
    elif isinstance(internal_value, set):
        return [convert_internal_value_to_dict(v) for v in list(internal_value)]
    elif hasattr(internal_value, "__dict__"):
        return convert_internal_value_to_dict(internal_value.__dict__)
    else:
        return internal_value


def to_decimal(value):
    if isinstance(value, Decimal):
        return value

    value = value if value is not None else 0
    return Decimal(value)


def to_int(value):
    if isinstance(value, int):
        return value
    return int(value) if value is not None else 0


def encode_uid(pk):
    return force_str(urlsafe_base64_encode(force_bytes(pk)))


def decode_uid(pk):
    return force_str(urlsafe_base64_decode(pk))


def convert_decimal_to_string(data):
    if isinstance(data, dict):
        return {k: convert_decimal_to_string(v) for k, v in data.items()}
    if isinstance(data, list):
        return [convert_decimal_to_string(i) for i in data]
    if isinstance(data, Decimal):
        return format(data, ".6f")
    return data


class UniqueCharField(serializers.CharField):
    """
    Custom CharField that automatically adds a UniqueValidator.
    """

    def __init__(self, queryset, message="This value already exists.", *args, **kwargs):
        # Adding the UniqueValidator automatically to the field
        self.validators.append(UniqueValidator(queryset=queryset, message=message))
        super().__init__(*args, **kwargs)
