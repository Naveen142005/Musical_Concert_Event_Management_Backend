from fastapi import UploadFile
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[int] = None
    password: str
    role_id: int = 2  # Default to customer


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[int]
    status: bool
    
    class Config:
        from_attributes = True


class LoginUser(BaseModel):
    email: str
    password: str


class UserDetailsUpdate(BaseModel):
    gender: Optional[str] = None
    dob: Optional[date] = None 
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    profile_image: Optional[str] = None