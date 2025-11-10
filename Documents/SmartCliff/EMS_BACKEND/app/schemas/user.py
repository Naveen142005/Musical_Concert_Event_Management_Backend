from typing import Literal
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

from uuid import UUID

from sqlalchemy import literal


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: int
    role: Literal["Admin", "Organizer", "Audience"] = Field(...)
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: int
    role_id: int
    status: bool

    class Config:
        from_attributes = True 

class LoginUser(BaseModel):
    email: EmailStr
    password: str





# ---------- Update Profile ----------
class UserUpdate(BaseModel):
    gender: Optional[str]
    dob: Optional[date]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]

# ---------- Password ----------
class ChangePassword(BaseModel):
    old_password: str
    new_password: str

class ResetPassword(BaseModel):
    email: EmailStr
    new_password: str

# ---------- Role Update (Admin) ----------
class RoleUpdate(BaseModel):
    user_id: int
    role_id: int

# ---------- Response ----------
class UserDetailsResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[int]
    gender: Optional[str]
    dob: Optional[date]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    role_id: int
    status: bool

    class Config:
        orm_mode = True
