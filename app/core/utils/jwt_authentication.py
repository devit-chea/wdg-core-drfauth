from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication

from django.conf import settings


class JWTCookieStatelessAuthentication(JWTStatelessUserAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT["ACCESS_COOKIE"])

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token
