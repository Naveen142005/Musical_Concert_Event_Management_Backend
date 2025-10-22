from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate
from datetime import date
from fastapi import HTTPException

class UserCRUD:
    def create_user(self, db: Session, user: UserCreate):

        
        
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        role = db.query(Role).filter((Role.name) == (user.role).lower()).first()
        
        if not role:
            raise HTTPException(status_code=400, detail=f"Invalid role: {user.role}")

        
        new_user = User(
            name=user.name,
            email=user.email,
            phone=user.phone,
            password=user.password,
            role_id=role.role_id,
            created_at=date.today(),
            status=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

user_crud = UserCRUD()
