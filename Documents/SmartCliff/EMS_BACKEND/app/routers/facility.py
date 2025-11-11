from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.auth.auth_utils import role_requires
from app.models.enum import SlotEnum, SortOrder
from app.services import facility
from app.dependencies import db
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Union
from app.dependencies import db
from app.schemas.facility import *
from fastapi import APIRouter, Form, Query, UploadFile, File, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.models.enum import EventStatus, PaymentStatus, SlotEnum
from app.dependencies import db
from app.schemas.payment import CancelEventRequest
from app.services.facility import facility_service
from app.services.events import event_service
from app.services.ticket import ticket_service
from app.utils.common import create_error
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.facility import facility_curd
from app.schemas.facility import (
    VenueBase, VenueResponse, VenueUpdate,
    BandBase, BandResponse, BandUpdate,
    DecorationBase, DecorationResponse, DecorationUpdate,
    SnackBase, SnackResponse, SnackUpdate
)
from typing import List

router = APIRouter(prefix="/facilities")

service = facility.FacilityGettingService()

show_route = APIRouter(tags=["View Facility"])

@show_route.get("/get_venues")
def get_all_venues(
    name: str | None = Query(None, description="Show venues only by the Names."),
    location: str | None = Query(None, description="Show venues only from this location (can match partly)."),
    min_capacity: int | None = Query(None, description="Show venues with at least this much capacity."),
    max_price: float | None = Query(None, description="Show only items with price less than or equal to this value."),
    sort_by: str | None = Query(None, description="Sort by this column name (like price, name, or capacity)."),
    order: SortOrder = Query(SortOrder.asc, description="Sort order — 'asc' for ascending, 'desc' for descending."),
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Organizer", "Audience"))
):
    model_dict = {
        "name": name,
        "location": location,
        "min_capacity": min_capacity,
        "max_price": max_price,
        "sort_by": sort_by,
        "order": order
    }
    return service.get_venues(db, model_dict)


@show_route.get("/get_bands")
def get_all_bands(
    name: str | None = Query(None, description="Filter bands by name."),
    genre: str | None = Query(None, description="Filter bands by genre."),
    member_count: int | None = Query(None, description="Filter bands by member count."),
    max_price: float | None = Query(None, description="Show only bands with price less than or equal to this value."),
    sort_by: str | None = Query(None, description="Sort by this column name (like price, name, or member_count)."),
    order: SortOrder = Query(SortOrder.asc, description="Sort order — 'asc' or 'desc'."),
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Organizer", "Audience"))

):
    model_dict = {
        "name": name,
        "genre": genre,
        "member_count": member_count,
        "max_price": max_price,
        "sort_by": sort_by,
        "order": order
    }
    return service.get_bands(db, model_dict)


@show_route.get("/get_decorations")
def get_all_decorations(
    name: str | None = Query(None, description="Filter decorations by name."),
    type: str | None = Query(None, description="Filter decorations by type."),
    max_price: float | None = Query(None, description="Show only decorations with price less than or equal to this value."),
    sort_by: str | None = Query(None, description="Sort by this column name (like price or name)."),
    order: SortOrder = Query(SortOrder.asc, description="Sort order — 'asc' or 'desc'."),
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Organizer", "Audience"))

):
    model_dict = {
        "name": name,
        "type": type,
        "max_price": max_price,
        "sort_by": sort_by,
        "order": order
    }
    return service.get_decorations(db, model_dict)


@show_route.get("/get_snacks")
def get_all_snacks(
    price: float | None = Query(None, description="Filter snacks by price."),
    sort_by: str | None = Query(None, description="Sort by this column name (like price or id)."),
    order: SortOrder = Query(SortOrder.asc, description="Sort order — 'asc' or 'desc'."),
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Organizer", "Audience"))

):
    model_dict = {
        "price": price,
        "sort_by": sort_by,
        "order": order
    }
    return service.get_snacks(db, model_dict)

@show_route.get("/facility/")
def check_facility_available(
    id: int = Query(..., description="Facility ID"),
    facility_name: str = Query(..., description="Name of the facility (venue/band/decoration)"),
    date: date = Query(..., description="Expected date of the facility (YYYY-MM-DD)"),
    slot: SlotEnum = Query(..., description="Slot of the facility (Morning/Afternoon/Night)"),
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Organizer"))

):
    
    if id <= 0:
        create_error('Provide valid facility Id')
    
    res =  facility_service.check_avaiable(db, id, facility_name, date, slot)
    if not res:
        return {"res": True , "mes" :f'{facility_name} id_{id} is available on {date}'}
    else:
        return {"res": False , "mes" :f'{facility_name} id_{id} is not available on {date}'}

@show_route.get("/booked-events")
def get_booked_facility_events(
    facility_type_id: int = Query(..., gt=0, description="Valid facility type ID"),
    facility_id: int = Query(..., gt=0, description="Valid facility ID"),
    start_date: date = Query(..., description="Start date for filtering bookings"),
    end_date: date = Query(..., description="End date for filtering bookings"),
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Admin"))

):
    events = facility_service.get_facility_bookings(db, facility_type_id, facility_id, start_date, end_date)
    
    if not events:
        raise HTTPException(status_code=404, detail="No events found for this facility within the given date range")
    
    return events



venue_route = APIRouter(tags=["Venues"])
# ========== VENUES ==========
@venue_route.post("/venues", response_model=VenueResponse)
def create_venue(data: VenueBase, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    return facility_curd.create_facility(db_session, 1, data.dict())



@venue_route.get("/venues/{venue_id}", response_model=dict)
def get_venue(venue_id: int, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    facility = facility_curd.get_facility_by_id(db_session, 1, venue_id)
    if not facility:
        raise HTTPException(404, "Venue not found")
    return facility


@venue_route.put("/venues/{venue_id}", response_model=dict)
def update_venue(venue_id: int, data: VenueUpdate, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    facility = facility_curd.update_facility(db_session, 1, venue_id, data.dict(exclude_unset=True))
    if not facility:
        raise HTTPException(404, "Venue not found")
    return facility


@venue_route.put("/venues/{venue_id}/image")
async def update_venue_image(
    venue_id: int,
    image: Union[UploadFile, str, None] = File(...),
    db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))
):
    """Update venue image"""
   
    return await facility_curd.update_facility_image(db_session, 1, venue_id, image=image)


@venue_route.delete("/venues/{venue_id}")
def delete_venue(venue_id: int, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    facility = facility_curd.delete_facility(db_session, 1, venue_id)
    if not facility:
        raise HTTPException(404, "Venue not found")
    return {"message": "Venue deleted successfully"}


band_route = APIRouter(tags=["Bands"])
# ========== BANDS ==========
@band_route.post("/bands", response_model=BandResponse)
def create_band(data: BandBase, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    return facility_curd.create_facility(db_session, 2, data.dict())




@band_route.get("/bands/{band_id}", response_model=dict)
def get_band(band_id: int, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    facility = facility_curd.get_facility_by_id(db_session, 2, band_id)
    if not facility:
        raise HTTPException(404, "Band not found")
    return facility


@band_route.put("/bands/{band_id}", response_model=dict)
def update_band(band_id: int, data: BandUpdate, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    facility = facility_curd.update_facility(db_session, 2, band_id, data.dict(exclude_unset=True))
    if not facility:
        raise HTTPException(404, "Band not found")
    return facility


@band_route.put("/bands/{band_id}/image")
async def update_band_image(
    band_id: int,
    image: Union[UploadFile, str, None] = File(...),
    db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))
):
    """Update band image"""
    
    
    return await facility_curd.update_facility_image(db_session, 2, band_id, image=image)


@band_route.delete("/bands/{band_id}")
def delete_band(band_id: int, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    facility = facility_curd.delete_facility(db_session, 2, band_id)
    if not facility:
        raise HTTPException(404, "Band not found")
    return {"message": "Band deleted successfully"}


decor_route = APIRouter(tags=["Decorations"])
# ========== DECORATIONS ==========
@decor_route.post("/decorations", response_model=DecorationResponse)
def create_decoration(data: DecorationBase, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    return facility_curd.create_facility(db_session, 3, data.dict())



@decor_route.get("/decorations/{decoration_id}", response_model=dict)
def get_decoration(decoration_id: int, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    facility = facility_curd.get_facility_by_id(db_session, 3, decoration_id)
    if not facility:
        raise HTTPException(404, "Decoration not found")
    return facility


@decor_route.put("/decorations/{decoration_id}", response_model=dict)
def update_decoration(decoration_id: int, data: DecorationUpdate, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    facility = facility_curd.update_facility(db_session, 3, decoration_id, data.dict(exclude_unset=True))
    if not facility:
        raise HTTPException(404, "Decoration not found")
    return facility


@decor_route.put("/decorations/{decoration_id}/image")
async def update_decoration_image(
    decoration_id: int,
    image: Union[UploadFile, str, None] = File(...),
    db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))
):

    
    return await facility_curd.update_facility_image(db_session, 3, decoration_id, image=image)


@decor_route.delete("/decorations/{decoration_id}")
def delete_decoration(decoration_id: int, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    facility = facility_curd.delete_facility(db_session, 3, decoration_id)
    if not facility:
        raise HTTPException(404, "Decoration not found")
    return {"message": "Decoration deleted successfully"}


scank_route = APIRouter(tags=["Scnaks"])
# ========== SNACKS ==========
@scank_route.post("/snacks", response_model=SnackResponse)
def create_snack(data: SnackBase, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    return facility_curd.create_facility(db_session, 4, data.dict())

@scank_route.get("/snacks/{snack_id}", response_model=dict)
def get_snack(snack_id: int, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    facility = facility_curd.get_facility_by_id(db_session, 4, snack_id)
    if not facility:
        raise HTTPException(404, "Snack not found")
    return facility

@scank_route.put("/snacks/{snack_id}", response_model=dict)
def update_snack(snack_id: int, data: SnackUpdate, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    facility = facility_curd.update_facility(db_session, 4, snack_id, data.dict(exclude_unset=True))
    if not facility:
        raise HTTPException(404, "Snack not found")
    return facility

@scank_route.put("/snacks/{snack_id}/image")
async def update_snack_image(
    snack_id: int,
    image: Union[UploadFile, str, None] = File(...),
    db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))
):
    """Update snack image"""

    
    return await facility_curd.update_facility_image(db_session, 4, snack_id, image=image)


@scank_route.delete("/snacks/{snack_id}")
def delete_snack(snack_id: int, db_session: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    facility = facility_curd.delete_facility(db_session, 4, snack_id)
    if not facility:
        raise HTTPException(404, "Snack not found")
    return {"message": "Snack deleted successfully"}

router.include_router(show_route)
router.include_router(venue_route)
router.include_router(band_route)
router.include_router(decor_route)
router.include_router(scank_route)