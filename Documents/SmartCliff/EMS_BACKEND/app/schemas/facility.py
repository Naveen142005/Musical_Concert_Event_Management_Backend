from datetime import date
from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.enum import FacilityStatus


# =========================
# VENUE SCHEMAS
# =========================
class VenueBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    location: str = Field(..., min_length=2, max_length=200)
    capacity: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    status: Optional[FacilityStatus] = FacilityStatus.AVAILABLE


class VenueUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    location: Optional[str] = Field(None, min_length=2, max_length=200)
    capacity: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    status: Optional[FacilityStatus] = None


class VenueResponse(VenueBase):
    id: int

    class Config:
        orm_mode = True


# =========================
# BAND SCHEMAS
# =========================
class BandBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    genre: Optional[str] = None

    member_count: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    status: Optional[FacilityStatus] = FacilityStatus.AVAILABLE


class BandUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    genre: Optional[str] = None

    member_count: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    status: Optional[FacilityStatus] = None


class BandResponse(BandBase):
    id: int

    class Config:
        orm_mode = True


# =========================
# DECORATION SCHEMAS
# =========================
class DecorationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    type: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    status: Optional[FacilityStatus] = FacilityStatus.AVAILABLE


class DecorationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    type: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    status: Optional[FacilityStatus] = None


class DecorationResponse(DecorationBase):
    id: int

    class Config:
        orm_mode = True


# =========================
# SNACK SCHEMAS
# =========================
class SnackBase(BaseModel):
    snacks: List[str] = Field(..., description="List of snack names")
    price: Optional[float] = Field(None, gt=0)


class SnackUpdate(BaseModel):
    snacks: Optional[List[str]] = None
    price: Optional[float] = Field(None, gt=0)


class SnackResponse(SnackBase):
    id: int

    class Config:
        orm_mode = True



class FacilityBookingFilter(BaseModel):
    facility_type_id: int = Field(..., gt=0, description="Valid facility type ID")
    facility_id: int = Field(..., gt=0, description="Valid facility ID")
    start_date: date = Field(..., description="Start date for filtering bookings")
    end_date: date = Field(..., description="End date for filtering bookings")

class FacilityBookingResponse(BaseModel):
    event_id: int
    name: str
    event_date: date
    created_at: str
