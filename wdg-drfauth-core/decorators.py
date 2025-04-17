import jwt
from functools import wraps
from django.http import JsonResponse
from jwt import ExpiredSignatureError, InvalidTokenError
from django.conf import settings
from .constants import PermissionOption
from .selectors import FetchPermissionSelector
from .utils import parse_verify_key


def is_permission_denied_or_needs_approval(permissions, codename):
    # Check if permissions or codename is None
    if permissions is None or codename is None:
        raise ValueError("Permissions list and codename cannot be None.")

    # Iterate through the permissions to check for the codename
    for perm in permissions:
        # Check if perm is None, just in case
        if perm is None:
            continue

        if perm.get("codename") == codename:
            perm_type = perm.get("type")
            if perm_type == PermissionOption.DENIED:
                raise PermissionError(f"Access denied for permission: {codename}")
            elif perm_type == PermissionOption.APPROVAL_REQUIRED:
                return f"Permission {codename} Approval required before proceeding."
            else:
                return None  # allowed

        # Recursively check children if they exist
        if perm.get("children"):
            result = is_permission_denied_or_needs_approval(perm["children"], codename)
            if result is not None:
                return result

    # Return None if codename is not found in the permissions
    return None


def is_permission_denied_or_needs_approval_v2(permissions, codename):
    if permissions is None or codename is None:
        raise ValueError("Permissions list and codename cannot be None.")

    def search(permissions):
        for perm in permissions:
            if perm is None:
                continue

            if perm.get("codename") == codename:
                perm_type = perm.get("type")
                if perm_type == PermissionOption.DENIED:
                    raise PermissionError(f"Access denied for permission: {codename}")
                elif perm_type == PermissionOption.APPROVAL_REQUIRED:
                    return f"Permission {codename} approval required before proceeding."
                else:
                    return None  # allowed

            if perm.get("children"):
                result = search(perm["children"])
                if result is not None:
                    return result

        return None

    result = search(permissions)
    if result is None:
        raise PermissionError(
            f"Permission {codename} not found. Access denied by default."
        )

    return result


def is_permission_denied_or_needs_approval_v3(permissions, codename):
    if permissions is None or codename is None:
        raise ValueError("Permissions list and codename cannot be None.")

    def search(permissions):
        for perm in permissions:
            if perm is None:
                continue

            if perm.get("codename") == codename:
                perm_type = perm.get("type")
                if perm_type == PermissionOption.DENIED:
                    raise PermissionError(f"Access denied for permission: {codename}")
                elif perm_type == PermissionOption.APPROVAL_REQUIRED:
                    return PermissionOption.APPROVAL_REQUIRED
                elif perm_type == PermissionOption.ALLOWED:
                    return PermissionOption.ALLOWED

            if perm.get("children"):
                result = search(perm["children"])
                if result:
                    return result

        return None  # Continue searching

    result = search(permissions)

    if result == PermissionOption.ALLOWED:
        return None
    elif result == PermissionOption.APPROVAL_REQUIRED:
        return f"Permission {codename} approval required before proceeding."
    else:
        raise PermissionError(
            f"Permission {codename} not found. Access denied by default."
        )


def check_permission(required_permissions=None, required_type=PermissionOption.ALLOWED):
    """
    Decorator to check if the user has the required permission type.
    - required_type: Can be PermissionOption.ALLOWED, PermissionOption.APPROVAL_REQUIRED, or PermissionOption.DENIED.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            request = args[1] if hasattr(args[0], "__class__") else args[0]

            # TODO: Redis Cache to prevent hit the same endpoint
            permissions = FetchPermissionSelector(request).fetch_permissions()

            codename_to_check = required_permissions
            try:
                message = is_permission_denied_or_needs_approval_v3(
                    permissions, codename_to_check
                )
                # TODO: will remove after testing
                if message:
                    print(message)  # approval_required case
                else:
                    print("Permission is allowed.")

            except PermissionError as e:
                return JsonResponse({"detail": str(e)}, status=403)

            if message:
                token = request.headers.get("X-Approval-Token") or request.META.get(
                    "HTTP_X_APPROVAL_TOKEN"
                )

                if not token:
                    return JsonResponse(
                        {"detail": "Approval token required."}, status=401
                    )

                try:
                    public_key = parse_verify_key(settings.JWT_VERIFYING_KEY)

                    payload = jwt.decode(token, public_key, algorithms=["RS256"])
                    request.user_payload = payload  # Attach to request

                    # Normalize permissions into a list
                    required = required_permissions
                    if required:
                        if isinstance(required, str):
                            required = [required]

                        user_permissions = payload.get("permissions", [])
                        # To check if permission not matching
                        missing_perms = [
                            perm for perm in required if perm not in user_permissions
                        ]

                        if missing_perms:
                            return JsonResponse(
                                {
                                    "detail": f"Missing permissions: {', '.join(missing_perms)}"
                                },
                                status=403,
                            )

                except ExpiredSignatureError:
                    return JsonResponse({"detail": "Token expired."}, status=401)
                except InvalidTokenError:
                    return JsonResponse({"detail": "Invalid token."}, status=401)

            # return view_func(request, *args, **kwargs)
            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator
