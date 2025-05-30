import jwt
from django.conf import settings


def parse_verify_key(key: str):
    if not key:
        return None
    return key.replace(r"\n", "\n")


def jwt_decode_rs256_token(token, public_key):
    try:
        decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def jwt_decode_hs256_token(token, secret_key):
    try:
        # Decode the token without verifying (since we only need the payload)
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def is_jwt_token_expired(token, alg="HS256"):
    if alg == "HS256":
        decoded_token = jwt_decode_hs256_token(
            token, secret_key=settings.SIMPLE_JWT["SIGNING_KEY"]
        )
    else:
        decoded_token = jwt_decode_rs256_token(token)

    if not decoded_token:
        return False
