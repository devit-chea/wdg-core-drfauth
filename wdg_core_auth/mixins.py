import jwt
from django.conf import settings
from django.http import JsonResponse
from jwt import ExpiredSignatureError, InvalidTokenError
from .decorators import is_permission_denied_or_needs_approval_v3
from .utils import parse_verify_key
from .selectors import FetchPermissionSelector

class ActionPermissionMixin:
    action_permissions = {}  # Define this in your view class

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        action = getattr(self, 'action', None)  # DRF ViewSets have `action`
        codename = self.action_permissions.get(action)

        if not codename:
            return  # Skip permission check if no codename specified

        permissions = FetchPermissionSelector(request).fetch_permissions()
        
        try:
            message = is_permission_denied_or_needs_approval_v3(permissions, codename)

            if message:  # approval_required
                token = request.headers.get("X-Approval-Token") or request.META.get(
                    "HTTP_X_APPROVAL_TOKEN"
                )

                if not token:
                    return JsonResponse(
                        {"detail": "Approval token required."}, status=401
                    )

                public_key = parse_verify_key(settings.JWT_VERIFYING_KEY)
                
                payload = jwt.decode(token, public_key, algorithms=["RS256"])
                request.user_payload = payload

                user_permissions = payload.get("permissions", [])
                if codename not in user_permissions:
                    return PermissionError(f"Missing permission: {codename}")

        except PermissionError as e:
            return JsonResponse({"detail": f"{str(e)}"}, status=401)
        except ExpiredSignatureError:
            return JsonResponse({"detail": "Approval Token expired."}, status=401)
        except InvalidTokenError:
            return JsonResponse({"detail": "Approval Invalid token."}, status=401)
