
import hashlib
import hmac
import secrets

from app.core.jwt import SECRET_KEY


def generate_csrf_token() -> str:
    """
    Generate a signed CSRF token using a random value
    and the application's existing secret key.
    """
    random_value = secrets.token_urlsafe(32)

    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        random_value.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return f"{random_value}.{signature}"


def validate_csrf_token(
    cookie_token: str | None,
    header_token: str | None
) -> bool:
    """
    Validate that the CSRF cookie and request header match
    and that the token has a valid HMAC signature.
    """
    if not cookie_token or not header_token:
        return False

    if not hmac.compare_digest(cookie_token, header_token):
        return False

    try:
        random_value, supplied_signature = cookie_token.rsplit(".", 1)
    except ValueError:
        return False

    if not random_value or not supplied_signature:
        return False

    expected_signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        random_value.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        supplied_signature,
        expected_signature
    )
