from fastapi import Depends, Response, HTTPException, status
from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from pytest import Session
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.config import settings
from jose import JWTError, jwt

from app.dependencies import db
from app.models.user import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login") 

# ✅ Create tokens and set refresh cookie
def generate_tokens(user_data: dict, response: Response):
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # ✅ Set True in production
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ✅ Refresh access token using cookie
def refresh_access_token(response: Response, refresh_token: str):
    try:
        payload = verify_token(refresh_token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_data = {"username": payload.get("username"), "role": payload.get("role")}
    return generate_tokens(user_data, response)

# adjust path if different

# ===================================================
# Decode & Verify Token
# ===================================================
def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token=token)
    return payload  # returns user payload

def admin_required(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def role_requires(*roles):
    def check(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{roles} access required"
            )
        return current_user
    return check