from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication


class CustomIsAuthenticated(IsAuthenticated):

    def has_permission(self, request, view):
        """
        1. If `user_type=anonymous` in the token, allow access.
        2. Otherwise, use the built-in `has_permission` method.
        """
        user_type = getattr(request.user, "user_type", None)

        if user_type and user_type == "anonymous_user":
            return True  # Allow access for anonymous users

        return super().has_permission(request, view)  # Default behavior


class CustomJWTStatelessUserAuthentication(JWTStatelessUserAuthentication):

    def get_user(self, validated_token):
        """
        Stateless User Authentication for anonymous user for some use case like
        E-Menu product listing(E-Menu QR code scan).

        1. If `user_type=anonymous`, return a mock anonymous user with metadata.
        2. Otherwise, use the built-in `get_user` method for normal user authentication.
        """
        user_type = str(validated_token.get("user_type"))

        if user_type == "anonymous_user":
            company_id = validated_token.get("company_id")
            branch_id = validated_token.get("branch_id")
            table_code = validated_token.get("table_code")
            customer_id = validated_token.get("customer_id")
            if not all([company_id, branch_id, user_type]):
                raise AuthenticationFailed("Invalid anonymous token.")

            # Create an anonymous user-like object

            user = type(
                "AnonymousUser",
                (),
                {
                    "is_authenticated": False,
                    "company_id": company_id,
                    "branch_id": branch_id,
                    "table_code": table_code,
                    "user_type": user_type,
                    "customer_id": customer_id,
                },
            )()
            return user

        # If user_type is missing or not "anonymous", use the built-in method
        return super().get_user(validated_token)
