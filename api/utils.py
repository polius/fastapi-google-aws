import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request

SECRET_KEY = os.getenv("SECRET_KEY")

def create_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now(timezone.utc) + timedelta(minutes=5)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm='HS512')

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=['HS512'])

def require_auth(request: Request):
    """Return decoded user data or None if not authenticated."""
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        return decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token not valid")
