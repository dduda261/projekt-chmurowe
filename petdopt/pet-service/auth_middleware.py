import jwt
from jwt import PyJWKClient, InvalidTokenError, ExpiredSignatureError
from functools import wraps
from flask import request, jsonify

KEYCLOAK_REALM = "petdopt"
KEYCLOAK_URL = f"http://localhost:8081/realms/{KEYCLOAK_REALM}"
JWKS_URL = f"{KEYCLOAK_URL}/protocol/openid-connect/certs"
ISSUER = KEYCLOAK_URL
AUDIENCE = ["petdopt-frontend"]

jwks_client = PyJWKClient(JWKS_URL)

def get_token_auth_header():
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise Exception("Authorization header is missing")

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise Exception("Authorization header must start with Bearer")
    elif len(parts) == 1:
        raise Exception("Token not found")
    elif len(parts) > 2:
        raise Exception("Authorization header must be 'Bearer <token>'")

    return parts[1]

def verify_jwt(token):
    signing_key = jwks_client.get_signing_key_from_jwt(token).key
    payload = jwt.decode(
        token,
        signing_key,
        algorithms=["RS256"],
        audience=AUDIENCE,
        issuer=ISSUER,
    )
    print("Decoded JWT payload:", payload)
    return payload

def requires_auth(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                payload = verify_jwt(token)

                user_roles = payload.get("realm_access", {}).get("roles", [])

                if allowed_roles and not any(role in user_roles for role in allowed_roles):
                    return jsonify({"msg": "Unauthorized – role missing"}), 403

                request.user = payload
                return f(*args, **kwargs)

            except ExpiredSignatureError:
                return jsonify({"msg": "Token wygasł"}), 401
            except InvalidTokenError as e:
                return jsonify({"msg": f"Nieprawidłowy token: {str(e)}"}), 401
            except Exception as e:
                return jsonify({"msg": f"Błąd uwierzytelniania: {str(e)}"}), 401

        return wrapper
    return decorator
