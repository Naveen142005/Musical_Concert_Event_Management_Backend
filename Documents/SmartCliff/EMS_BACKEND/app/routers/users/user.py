from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse

from app.crud.Users.user import user_crud
from dependencies import db

router = APIRouter()

@router.post("/signup", response_model=UserResponse)

def signup(user_data: UserCreate, db: Session = Depends(db.get_db)):
    return user_crud.create_user(db, user_data)
