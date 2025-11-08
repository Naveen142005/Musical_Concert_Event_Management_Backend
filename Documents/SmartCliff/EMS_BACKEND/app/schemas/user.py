from typing import Literal
from pydantic import BaseModel, EmailStr, Field
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
