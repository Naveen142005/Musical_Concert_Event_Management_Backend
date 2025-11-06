from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.enum import SlotEnum, SortOrder
from app.services import facility
from app.dependencies import db

import enum
from fastapi import APIRouter, Form, Query, UploadFile, File, Depends, HTTPException
from typing import Optional, Literal
from datetime import date, datetime
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.models.events import Event
from app.models.facilities import Venues
from app.schemas.event import EventBase, EventResponse, RescheduleEventRequest
from app.models.enum import EventStatus, PaymentStatus, SlotEnum
from app.dependencies import db
from app.crud.event import event, event_crud
from app.schemas.payment import CancelEventRequest
from app.services.facility import facility_service
from app.services.events import event_service
from app.services.ticket import ticket_service
from app.utils.common import commit, create_error, insert_data, update_data

router = APIRouter(prefix="/facilities")
service = facility.FacilityGettingService()


@router.get("/venues")
def get_all_venues(
    name: str | None = Query(None, description="Show venues only by the Names."),
    location: str | None = Query(None, description="Show venues only from this location (can match partly)."),
    min_capacity: int | None = Query(None, description="Show venues with at least this much capacity."),
    max_price: float | None = Query(None, description="Show only items with price less than or equal to this value."),
    sort_by: str | None = Query(None, description="Sort by this column name (like price, name, or capacity)."),
    order: SortOrder = Query(SortOrder.asc, description="Sort order — 'asc' for ascending, 'desc' for descending."),
    db: Session = Depends(db.get_db)
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


@router.get("/bands")
def get_all_bands(
    name: str | None = Query(None, description="Filter bands by name."),
    genre: str | None = Query(None, description="Filter bands by genre."),
    member_count: int | None = Query(None, description="Filter bands by member count."),
    max_price: float | None = Query(None, description="Show only bands with price less than or equal to this value."),
    sort_by: str | None = Query(None, description="Sort by this column name (like price, name, or member_count)."),
    order: SortOrder = Query(SortOrder.asc, description="Sort order — 'asc' or 'desc'."),
    db: Session = Depends(db.get_db)
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


@router.get("/decorations")
def get_all_decorations(
    name: str | None = Query(None, description="Filter decorations by name."),
    type: str | None = Query(None, description="Filter decorations by type."),
    max_price: float | None = Query(None, description="Show only decorations with price less than or equal to this value."),
    sort_by: str | None = Query(None, description="Sort by this column name (like price or name)."),
    order: SortOrder = Query(SortOrder.asc, description="Sort order — 'asc' or 'desc'."),
    db: Session = Depends(db.get_db)
):
    model_dict = {
        "name": name,
        "type": type,
        "max_price": max_price,
        "sort_by": sort_by,
        "order": order
    }
    return service.get_decorations(db, model_dict)


@router.get("/snacks")
def get_all_snacks(
    price: float | None = Query(None, description="Filter snacks by price."),
    sort_by: str | None = Query(None, description="Sort by this column name (like price or id)."),
    order: SortOrder = Query(SortOrder.asc, description="Sort order — 'asc' or 'desc'."),
    db: Session = Depends(db.get_db)
):
    model_dict = {
        "price": price,
        "sort_by": sort_by,
        "order": order
    }
    return service.get_snacks(db, model_dict)

@router.get("/facility/")
def check_facility_available(
    id: int = Query(..., description="Facility ID"),
    facility_name: str = Query(..., description="Name of the facility (venue/band/decoration)"),
    date: date = Query(..., description="Expected date of the facility (YYYY-MM-DD)"),
    slot: SlotEnum = Query(..., description="Slot of the facility (Morning/Afternoon/Night)"),
    db: Session = Depends(db.get_db)
):
    
    if id <= 0:
        create_error('Provide valid facility Id')
    
    res =  facility_service.check_avaiable(db, id, facility_name, date, slot)
    if not res:
        return {"res": True , "mes" :f'{facility_name} id_{id} is available on {date}'}
    else:
        return {"res": False , "mes" :f'{facility_name} id_{id} is not available on {date}'}