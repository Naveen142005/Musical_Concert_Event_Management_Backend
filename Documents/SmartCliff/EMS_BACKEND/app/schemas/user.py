from pydantic import BaseModel, EmailStr
from datetime import date

from uuid import UUID


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: int
    role: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: int
    role_id: UUID
    created_at: date
    status: bool

    class Config:
        from_attributes = True 
