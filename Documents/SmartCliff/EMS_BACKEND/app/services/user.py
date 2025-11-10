from argon2 import verify_password
from fastapi import HTTPException, Response, status
from pytest import Session
from app.auth.jwt_handler import create_access_token, create_refresh_token
from app.config import settings
from app.models.role import Role
from app.models.user import User, UserDetails
from app.schemas.user import LoginUser, UserUpdate
from passlib.context import CryptContext

from app.utils.common import *

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
class UserService:
    def login_user(self, db: Session, curr_user: LoginUser, response: Response):
        # Find user
        user_db = db.query(User).filter(User.email == curr_user.email).first()
        if not user_db:
            raise HTTPException(status_code=400, detail="Invalid Email")
        
        # Check password
        if not pwd_context.verify(curr_user.password, user_db.password):
            raise HTTPException(status_code=400, detail="Invalid Password")

        # Fetch role name (join Role table)
        role = db.query(Role).filter(Role.id == user_db.role_id).first()
        role_name = role.name if role else "unknown"

        # Prepare data for token
        user_data = {
            "id": user_db.id,
            "email": user_db.email,
            "role": role_name
        }

        # Create tokens
        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token(user_data)

        # Set refresh token cookie 🍪
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # ⚠️ change to True in production (for HTTPS)
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        # Return access token + user info
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_db.id,
                "name": user_db.name,
                "email": user_db.email,
                "role": role_name
            }
        }
    def get_user_by_id(self, db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Get role name
        role = db.query(Role).filter(Role.id == user.role_id).first()
        role_name = role.name if role else "unknown"

        # Return combined user info
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": role_name
        }
    
    # ========== UPDATE PROFILE ==========
    def update_profile_service(self,db: Session, user_id: int, data: UserUpdate):
        user = get_row(db, User, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        details = get_row(db, UserDetails, user_id=user_id)
        if not details:
            details = insert_data(db, UserDetails, user_id=user_id)

        update_data(db, User, User.id == user_id, name=data.name, phone=data.phone)
        update_data(
            db, UserDetails, UserDetails.user_id == user_id,
            gender=data.gender, dob=data.dob,
            city=data.city, state=data.state, country=data.country
        )
        commit(db)
        return {"message": "Profile updated successfully"}

    # ========== CHANGE PASSWORD ==========
    def change_password_service(self,db: Session, user_id: int, old_password: str, new_password: str):
        user = get_row(db, User, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(old_password, user.password):
            raise HTTPException(status_code=400, detail="Invalid old password")

        user.password = hash(new_password)
        commit(db)
        return {"message": "Password changed successfully"}

    # ========== RESET PASSWORD (direct by email) ==========
    def reset_password_service(self,db: Session, email: str, new_password: str):
        user = get_row(db, User, email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.password = hash(new_password)
        commit(db)
        return {"message": "Password reset successfully"}

    # ========== DEACTIVATE ACCOUNT ==========
    def deactivate_user_service(self,db: Session, user_id: int):
        user = get_row(db, User, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.status = False
        commit(db)
        return {"message": "Account deactivated successfully"}

    # ========== ADMIN ==========
    def get_all_users_service(self,db: Session):
        users = get_rows(db, User)
        return users

    def get_user_by_id_service(self,db: Session, user_id: int):
        user = get_row(db, User, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def update_user_role_service(self,db: Session, user_id: int, role_id: int):
        user = get_row(db, User, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.role_id = role_id
        commit(db)
        return {"message": "User role updated"}
    
user_service = UserService()