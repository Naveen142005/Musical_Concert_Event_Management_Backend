import enum
from fastapi import APIRouter, BackgroundTasks, Form, Query, UploadFile, File, Depends, HTTPException
from typing import Optional, Literal
from datetime import date, datetime
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.auth.auth_utils import role_requires
from app.models.events import Event
from app.models.facilities import Venues
from app.schemas.event import EventBase, EventResponse, RescheduleEventRequest
from app.models.enum import DateType, EventStatus, PaymentMode, PaymentStatus, SlotEnum
from app.dependencies import db
from app.crud.event import event, event_crud
from app.schemas.payment import CancelEventRequest
from app.services.facility import facility_service
from app.services.events import event_service
from app.services.ticket import ticket_service
from app.utils.common import commit, create_error, insert_data, update_data
from app.services.payment import payment_service
router = APIRouter()




@router.post('/create_new_event', response_model=EventResponse)
async def create_new_event(event_data:EventBase,  db:Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Organizer"))):
    new_event = EventBase(**event_data.model_dump())
    user_id = current_user["id"]
    return await event.create_new_event(event_data, user_id,db)
    

@router.patch("/update_banner")
def update_banner( 
        eventId: int = Query(..., description="Event Id"),
        banner: UploadFile = File(..., description="Update event Banner image if exist it overwrites"), db:Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Organizer"))):
    if eventId <= 0:
        create_error('Provide valid event Id')
    path = event_service.save_image(eventId, banner, db)
   
    return {"Status": "Image Inserted Successfully", "path": path}

@router.get('/show_banner')
def get_banner(
    event_id: int = Query(..., description='Event_id'),
    db: Session = Depends(db.get_db)
, current_user: dict = Depends(role_requires("Organizer"))):
    return event_service.get_banner(event_id, db)

    
@router.get("/events/{event_id}")
async def get_event_by_id(event_id: int, db: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Organizer"))):
    if event_id <= 0:
        create_error('Provide valid event Id')
    return await event_service.get_event_by_id(event_id, db) 



@router.get("/events/search")
def search_events(
    event_name: str | None = Query(None),
    facility_name: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    slot: SlotEnum = Query(None, description="Slot of the facility (Morning/Afternoon/Night)"),
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Audience"))

):
    return event_service.search_public_events(
        db, event_name, facility_name, start_date, end_date, min_price, max_price, slot
    )
 



@router.get('/my_bookings/upcoming')
async def get_my_upcoming_bookings(db:Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Organizer"))):
     user_id: int = current_user["id"] #Should be get from cookie or someWhere
     return await event_service.get_bookings(user_id,db,"upcoming")
 
@router.get('/my_bookings/past')
async def get_my_past_bookings(db:Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Organizer"))):
     user_id: int = current_user["id"] #Should be get from cookie or someWhere
     return await event_service.get_bookings(user_id,db,"past")
 
@router.get('/my_bookings/pending')
async def get_my_pending_bookings(db:Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Organizer"))):
     user_id: int = current_user["id"] #Should be get from cookie or someWhere
     return await event_service.get_bookings(user_id,db,"pending")

 
@router.get('/my_bookings/ongoing')
async def get_my_bookings(db:Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Organizer"))):
     user_id: int = current_user["id"] #Should be get from cookie or someWhere
     return await event_service.get_bookings(user_id,db,"ongoing")
 

@router.post('/pay_pending_amount/{event_id}')
async def pay_pending_amount (event_id:int, payment_mode: PaymentMode =  Query(PaymentMode.UPI, description="Payment mode"), db: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Organizer"))):
    user_id = current_user["id"] # fetch from cookie 
    print("helo")
    return await event_crud.pay_pending_amount(event_id, user_id,payment_mode, db)



@router.get('/facilities')
def check_facilities_available(
    slot: SlotEnum = Query(..., description="Slot of the facility (Morning/Afternoon/Night)"),
    venue_id: int | None = Query(None, description="venue ID"),
    band_id: int | None = Query(None, description="Band ID"),
    decoration_id: int | None = Query(None, description="Decoration ID"),
    no_days : int = Query(10, description="upto, how many days"),
    db: Session = Depends(db.get_db)
, current_user: dict = Depends(role_requires("Organizer"))): 
    
    
    return facility_service.get_facilities_available_dates(slot, venue_id, band_id, decoration_id, no_days, db)



@router.get('/get_reschedule_dates')
async def get_possible_reschedule_dates(
    eventId: int = Query(..., description="Event Id"),
    start_date: date = Query(..., description="Start date in YYYY-MM-DD "),
    end_date: date = Query(..., description="End date in YYYY-MM-DD "),
    slot: SlotEnum = Query(..., description="Slot of the facility (Morning/Afternoon/Night)"),
    db: Session = Depends(db.get_db)
, current_user: dict = Depends(role_requires("Organizer"))):
    if eventId <= 0:
        create_error('Provide valid event Id')
    return await event_service.get_possible_reschedule_dates(eventId, start_date, end_date, slot, db)
 

@router.patch('/reschedule_event')
async def reschedule_event(
    body: RescheduleEventRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(db.get_db)
, current_user: dict = Depends(role_requires("Organizer"))):
    #user id... see
    res = await event_crud.reshedule_event(
        body.event_id, current_user["id"], body.excepted_date, body.ticket_opening_date, body.slot,db, background_tasks
    )
    return res

@router.post("/event_cancel/{event_id}")
async def cancel_event(
    event_id: int,
    body: CancelEventRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Organizer"))):
    user_id = current_user["id"] # Fetch from cookine
    return await event_crud.cancel_event(event_id, db, body.reason, user_id, background_tasks)


@router.get("/booked-events")
async def get_booked_events(
    start_date: Optional[date] = Query(None, description="Filter from this date"),
    end_date: Optional[date] = Query(None, description="Filter until this date"),
    search: Optional[str] = Query(None, description="Global search across event fields"),
    status: Optional[EventStatus] = Query(None,
        description="Filter by status: upcoming, past, ongoing, rescheduled, cancelled"
    ),
    slot: SlotEnum = Query(None, description="Slot of the facility (Morning/Afternoon/Night)"),
    date_type: Optional[DateType] = Query(
        None,
        description="Filter by: booked_date or event_date"
    ),
    db: Session = Depends(db.get_db)
, current_user: dict = Depends(role_requires("Admin"))):
    # ✅ Validation
    print("==================")
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")
    print(slot , "====--")
    
    events = await event_service.get_booked_events_1(db, start_date, end_date, search, status, date_type, slot)


    if not events:
        raise HTTPException(status_code=404, detail="No events found")

    return events

@router.get('/view_ticket_details/{event_id}')
def get_ticket_details_for_event(event_id:int, db: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Organizer"))):
    return ticket_service.get_booked_ticket_details(db, event_id)


@router.get("/download/{event_id}")
def download_invoice(event_id: int, db: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Organizer"))):
    """Download invoice PDF for an event"""
    return event_service.get_invoice(event_id, db)