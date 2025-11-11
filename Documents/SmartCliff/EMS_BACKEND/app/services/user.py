from fastapi import HTTPException, Response, status
from sqlalchemy.orm import Session
from app.auth.jwt_handler import create_access_token, create_refresh_token
from app.config import settings
from app.models.role import Role
from app.models.user import User, UserDetails
from passlib.context import CryptContext
from app.schemas.user import *

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class UserService:
    
    def login_user(self, db: Session, curr_user: LoginUser, response: Response):
        """Login user"""
        user_db = db.query(User).filter(User.email == curr_user.email).first()
        if not user_db:
            raise HTTPException(status_code=400, detail="Invalid Email")
        
        if not pwd_context.verify(curr_user.password, user_db.password):
            raise HTTPException(status_code=400, detail="Invalid Password")
        
        role = db.query(Role).filter(Role.id == user_db.role_id).first()
        role_name = role.name if role else "unknown"
        
        user_data = {
            "id": user_db.id,
            "email": user_db.email,
            "role": role_name
        }
        
        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token(user_data)
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )
        
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
    
    
    def create_user(self, db: Session, user: UserCreate):
        """Create new user"""
        existing = db.query(User).filter(User.email == user.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = pwd_context.hash(user.password)
        
        new_user = User(
            name=user.name,
            email=user.email,
            phone=user.phone,
            password=hashed_password,
            role_id=user.role_id
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    
    def get_all_users(self, db: Session):
        """Get all users"""
        return db.query(User).all()
    
    
    def get_user_by_id(self, db: Session, user_id: int):
        """Get user by ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    
    def update_user(self, db: Session, user_id: int, user_data: UserUpdate):
        """Update user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user_data.name:
            user.name = user_data.name
        if user_data.phone:
            user.phone = user_data.phone
        
        db.commit()
        db.refresh(user)
        return user
    
   
    def update_details(self, db: Session, user_id: int, update_data: UserDetailsUpdate, profile_image_url: str = None):
        details = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
        if not details:
            details = UserDetails(user_id=user_id)
            db.add(details)
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(details, field, value)
        if profile_image_url:
            details.profile_image = profile_image_url
        
        db.commit()
        db.refresh(details)
        return details

    def get_user_details(self, db: Session, user_id: int):
        """Get user details by user ID"""
        return db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
    
    def update_profile_image(self, db: Session, user_id: int, image_url: str):
        details = db.query(UserDetails).filter(UserDetails.user_id == user_id).first()
        if not details:
            details = UserDetails(user_id=user_id)
            db.add(details)
        details.profile_image = image_url
        db.commit()
        db.refresh(details)
        return details


user_service = UserService()
