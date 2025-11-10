import os
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.auth.auth_utils import admin_required, decode_token, get_current_user, role_requires
from app.models.user import UserDetails
from app.schemas.user import ChangePassword, LoginUser, ResetPassword, RoleUpdate, UserCreate, UserResponse, UserUpdate
from app.crud.user import user_crud
from app.dependencies import db
from app.services.user import user_service
from app.utils.common import *
from app.auth.auth_utils import oauth2_scheme

UPLOAD_DIR = "uploads/profiles_photos"
router = APIRouter() 

@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(db.get_db)):
    return user_crud.create_user(db, user_data)
  


@router.post("/Login")
def login(
    res: Request,
    login_input: LoginUser,
    response: Response,
    db: Session = Depends(db.get_db)
):
    user_data = user_service.login_user(db, login_input, response)
    print ("--------------------")
    return {
            "name": user_data["user"]["name"],
            "access_token": user_data["access_token"]
        }
    

@router.get("/profile")
def get_user_profile(current_user: str = Depends(role_requires("Organizer, Audience")), db: Session = Depends(db.get_db)):
    
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = user_service.get_user_by_id(db, current_user["id"])
    return user


@router.post("/login")
def for_oauth_(
    response: Response,
    db: Session = Depends(db.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    # Convert form data into Pydantic object
    login_input = LoginUser(
        email=form_data.username,
        password=form_data.password
    )

    user_data = user_service.login_user(db, login_input, response)

    return {
        "access_token": user_data["access_token"],
        "token_type": "bearer",
        "user": user_data["user"]
    }
    


# ---------- 1️⃣ Update Profile ----------
@router.put("/update-profile")
def update_profile(
    data: UserUpdate,
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Organizer, Audience"))
):
    return user_service.update_profile_service(db, current_user["id"], data)

# ---------- 2️⃣ Change Password ----------
@router.put("/change-password")
def change_password(
    data: ChangePassword,
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Organizer, Audience"))
):
    return user_service.change_password_service(db, current_user["id"], data.old_password, data.new_password)

# ---------- 3️⃣ Reset Password ----------
@router.post("/reset-password")
def reset_password(data: ResetPassword, db: Session = Depends(db.get_db)):
    return user_service.reset_password_service(db, data.email, data.new_password)

# ---------- 4️⃣ Deactivate ----------
@router.put("/deactivate")
def deactivate_user(
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Organizer, Audience"))
):
    return user_service.deactivate_user_service(db, current_user["id"])

# ---------- 5️⃣ Upload Profile Picture ----------
@router.post("/upload-photo")
def upload_photo(
    file: UploadFile = File(...),
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Organizer, Audience"))
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    update_data(db, UserDetails, UserDetails.user_id == current_user["id"], profile_image=file_path)
    commit(db)
    return {"message": "Profile photo updated successfully", "path": file_path}

# ---------- ADMIN ENDPOINTS ----------
@router.get("/all")
def get_all_users(
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Admin"))
):
    return user_service.get_all_users_service(db)

@router.get("/{user_id}")
def get_user_by_id(
    user_id: int,
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Admin"))
):
    return user_service.get_user_by_id_service(db, user_id)

@router.put("/update-role")
def update_user_role(
    data: RoleUpdate,
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Admin"))
):
    return user_service.update_user_role_service(db, data.user_id, data.role_id)
