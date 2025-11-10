from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.schemas.user import LoginUser, UserCreate
from datetime import date
from passlib.hash import bcrypt 
from passlib.context import CryptContext
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class UserCRUD:
    #------------------Create User-------------------------------#
    
    def create_user(self, db: Session, user: UserCreate):
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        role = db.query(Role).filter((Role.name) == (user.role)).first()
        
        print(role)
        if not role:
            raise HTTPException(status_code=400, detail=f"Invalid role: {user.role}")
        
        new_user = User(
            name=user.name,
            email=user.email,
            phone=user.phone,
            password=pwd_context.hash(user.password),
            role_id=role.id,
            status=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
      
  
   #---------------------------Login User------------------------# 
    
    
        
user_crud = UserCRUD()
