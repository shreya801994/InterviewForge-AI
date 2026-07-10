from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

def get_user_or_ip(request: Request) -> str:
    """
    Key function to identify request source.
    Returns the authenticated user's ID if a valid Bearer token is present, 
    otherwise falls back to client IP address.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.strip().startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        try:
            from app.security import decode_access_token
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get("user_id")
                if user_id:
                    return f"user:{user_id}"
        except Exception:
            pass
    return get_remote_address(request)

# Create central limiter state
limiter = Limiter(key_func=get_user_or_ip)
