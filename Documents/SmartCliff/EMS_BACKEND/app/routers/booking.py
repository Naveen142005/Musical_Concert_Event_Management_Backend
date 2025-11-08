

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pytest import Session
from app.dependencies import db
from app.models.enum import BookingStatus, DateType, SlotEnum
from app.models.events import Event
from app.schemas.booking import BookingCreate, BookingResponse
from app.schemas.payment import CancelEventRequest
from app.services.booking import booking_service
from app.services.ticket import ticket_service
from app.crud.booking import booking_crud
from app.utils.common import get_row
from app.services.events import event_service
router = APIRouter()


@router.get('/get_events')
def get_public_events(db:Session = Depends(db.get_db)):
    return booking_service.get_public_events(db=db)

@router.get("/available/{event_id}")
def get_available_tickets(event_id: int, db: Session = Depends(db.get_db)):
    if event_id not in booking_service.get_pubilc_event_id(db):
        raise HTTPException(status_code=404, detail="This event is private event.")
    result = ticket_service.get_available_tickets_by_event(event_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="No tickets found for this event.")
    return result

@router.post("/book_event/", response_model=BookingResponse)
def book_event(booking_data: BookingCreate, db: Session = Depends(db.get_db)):
    if booking_data.event_id not in booking_service.get_pubilc_event_id(db):
        raise HTTPException(status_code=404, detail="This event is private event.")
    user_id = 8
    return booking_crud.create_booking(db, booking_data, user_id)    

@router.get('/upcoming_bookings')
def get_upcoming_bookings(db: Session = Depends(db.get_db)):
    user_id = 2  # fetch from cookie
    return booking_service.get_booking(user_id,db, "upcoming")

@router.get('/past_bookings')
def get_upcoming_bookings(db: Session = Depends(db.get_db)):
    user_id = 2  # fetch from cookie
    return booking_service.get_booking(user_id,db, "past")


@router.post("/booking_cancel/{Booking_id}")
def cancel_event(
    booking_id: int,
    body: CancelEventRequest,
    db: Session = Depends(db.get_db)
):
    user_id = 2
    
    return booking_crud.cancel_event(booking_id, db, body.reason, user_id)


@router.get("/events/search")
def search_events(
    event_name: str | None = Query(None),
    facility_name: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    slot: SlotEnum = Query(None, description="Slot of the facility (Morning/Afternoon/Night)"),
    db: Session = Depends(db.get_db)
):
    return event_service.search_public_events(
        db, event_name, facility_name, start_date, end_date, min_price, max_price, slot
    )
 



@router.get("/all")
def get_all_bookings(
    db: Session = Depends(db.get_db),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search by event name"),
    date_type: Optional[str] = Query(
        "booked_date",
        description="Dropdown option: booked_date or event_date",
        enum=["booked_date", "event_date"]
    ),
    status: Optional[BookingStatus] = Query(
        None,
        description="Filter by booking status",
        enum=[BookingStatus.BOOKED, BookingStatus.CANCELLED],
    ),
    sort_by: Optional[str] = Query(
        None,
        description="Sort dropdown: total_amount or total_tickets",
        enum=["total_amount", "total_tickets"],
    ),
):
    """
    Fetch all bookings with:
    - Date filter (booked_date or event_date)
    - Status filter (Booked/Cancelled)
    - Sorting (total_amount/total_tickets)
    - Search by event name
    """
    
    
    
    result = booking_service.get_all_bookings(
        db=db,
        start_date=start_date,
        end_date=end_date,
        search=search,
        date_type=date_type,
        status=status,
        sort_by=sort_by,
    )
    return result