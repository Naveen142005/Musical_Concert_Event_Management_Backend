from datetime import date, datetime
from fileinput import filename
import os
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from pydantic import EmailStr, Field
from sqlalchemy.orm import Session
from app.auth.auth_utils import role_requires, get_current_user
from app.dependencies import db
from app.services.user import user_service
from app.schemas.user import UserCreate, UserDetailsUpdate, UserUpdate, UserResponse, LoginUser

from typing import List, Union

from app.utils.common import get_image_url, get_url


router = APIRouter(tags=["Users"])



@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(db.get_db)):
    """Register new user - Public"""
    return user_service.create_user(db, user)


@router.post("/login")
def login(response: Response, username: str = Form(...), password: str = Form(...),  db: Session = Depends(db.get_db)):
    """Login user - Public"""
    user = LoginUser(email=username, password=password)
    return user_service.login_user(db, user, response)


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current logged-in user profile"""
    return user_service.get_user_by_id(db, current_user["id"])


@router.get("/me/details")
def get_my_details(
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Organizer", "Audience"))
):
    """Get current user's extra details"""
    details =  user_service.get_user_details(db, current_user["id"])
    if not details:
        raise HTTPException(404, "No details Found")
    return details


from fastapi import Body

@router.patch("/details/update")
async def update_my_details(
    update_data: UserDetailsUpdate = Body(...),
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Organizer", "Audience"))
):
    return user_service.update_details(db, current_user["id"], update_data, None)


@router.post("/details/upload-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Organizer", "Audience")),
):
    try:
        upload_dir = "uploads/profiles"
        os.makedirs(upload_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = os.path.splitext(file.filename)[1]
        file_name = f"{timestamp}{extension}"
        file_path = os.path.join(upload_dir, file_name)

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        image_url = f"/uploads/profiles/{file_name}"

        # Update user's profile image in DB
        user_service.update_profile_image(db, current_user["id"], image_url)

        # Return the complete image URL
        return {"image_url": get_url(image_url)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Organizer", "Audience"))
):
    """Change password for logged-in user"""
    
    user = user_service.get_user_by_id(db, current_user['id'])
    if (old_password == new_password):
        raise HTTPException (404, "Both are same password. Try to give different")
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    
    if not pwd_context.verify(old_password, user.password):
        raise HTTPException(status_code=400, detail="Old password incorrect")
    user.password = pwd_context.hash(new_password)
    db.commit()
    return {"message": "Password changed successfully"}

#Admin Routes
router_admin = APIRouter(tags=["Admin action"])

@router_admin.get("/", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Admin"))
):
    """Get all users - Admin only"""
    return user_service.get_all_users(db)


@router_admin.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Admin"))
):
    """Get user by ID - Admin only"""
    return user_service.get_user_by_id(db, user_id)

@router_admin.patch("/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Admin"))
):
    """Deactivate user (set status=False) - Admin only"""
    user = user_service.get_user_by_id(db, user_id)
    if user.role_id == 1:
        raise HTTPException (404, "Admin can not deactivate a admin")
    user.status = False
    db.commit()
    db.refresh(user)
    return {"message": "User deactivated", "id": user.id}


@router_admin.patch("/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Admin"))
):
    """Reactivate user (set status=True) - Admin only"""
    user = user_service.get_user_by_id(db, user_id)
    if user.role_id == 1:
        raise HTTPException (404, "Admin can not activate a admin")
    user.status = True
    db.commit()
    db.refresh(user)
    return {"message": "User activated", "id": user.id}





