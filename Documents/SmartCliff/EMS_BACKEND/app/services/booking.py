import os
import uuid
from datetime import date, datetime as dayTime, timedelta, timezone
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pytest import Session
from sqlalchemy import String, and_, case, cast, desc, func, or_
from app.models.enum import BookingStatus, EventStatus
from app.models.events import Event
from app.models.tickets import Tickets
from app.models.user import User
from app.utils.common import create_error, get_row, get_rows, update_data
from app.services.ticket import ticket_service
from app.services.facility import facility_service
from app.models.bookings import BookingDetails, Bookings
IST = timezone(timedelta(hours=5, minutes=30)) 
class BookingService:
    def get_pubilc_event_id(_,db:Session):
        data = (db.query(Event)
                .filter(Event.ticket_enabled == True)
                .filter(Event.status.in_([EventStatus.BOOKED, EventStatus.RESCHEDULED]))).all()
        res = [i.id for i in data]
        return res
        
    
    def get_public_events(self, db: Session):
        data =  get_rows(db, Event, ticket_enabled = True)
        data = (db.query(Event)
                .filter(Event.ticket_enabled == True)
                .filter(Event.status.in_([EventStatus.BOOKED, EventStatus.RESCHEDULED]))).all()
        res = [
            {
                "id": i.id,
                "name": i.name,
                "slot": i.slot,
                "event_date": i.event_date,
                "ticket_open_date": i.ticket_open_date,
                "description": i.description,
                "banner": i.banner,
            }
            for i in data
        ]
        return res



    def get_booking(self, user_id: int, db: Session, status: str):
        if status not in ["upcoming", "past"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status type. Must be 'upcoming' or 'past'."
            )

        # Upcoming → only BOOKED
        if status == "upcoming":
            bookings = (
                db.query(Bookings)
                .filter(Bookings.user_id == user_id, Bookings.status == BookingStatus.BOOKED)
                .all()
            )
        else:  # past → cancelled / completed / refunded
            bookings = (
                db.query(Bookings)
                .filter(
                    Bookings.user_id == user_id,
                    or_(
                        Bookings.status == BookingStatus.CANCELLED,
                        Bookings.status == BookingStatus.COMPLETED,
                        Bookings.status == BookingStatus.REFUNDED,
                    ),
                )
                .all()
            )

        if not bookings:
            raise HTTPException(
                status_code=404,
                detail=f"No {status} bookings found for this user."
            )

        result = []
        for booking in bookings:
            # Use relationship instead of get_rows()
            details = booking.booking_details or []

            result.append({
                "booking_id": booking.id,
                "event_id": booking.event_id,
                "booked_date": booking.booked_date,
                "total_tickets": booking.total_tickets,
                "total_amount": booking.total_amount,
                "status": booking.status.name,
                "details": [
                    {
                        "ticket_type": d.ticket_type,
                        "quantity": d.quantity,
                        "sub_total": d.sub_total
                    } for d in details
                ]
            })

        return result
    
    def get_all_bookings(self, db, start_date=None, end_date=None, search=None, date_type=None, status=None, sort_by=None):
        
        def validate_date(date_str: str, field_name: str):
            try:
                return dayTime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid {field_name}: '{date_str}'. Expected format: YYYY-MM-DD",
                )

        if start_date:
            start_date = validate_date(start_date, "start_date")

        if end_date:
            end_date = validate_date(end_date, "end_date")

        # ✅ Validate date range
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=400, detail="start_date cannot be greater than end_date."
            )

        # ✅ Validate sort_by and date_type are supported (already limited by enum in Query)
        if date_type not in ["booked_date", "event_date"]:
            raise HTTPException(status_code=400, detail="Invalid date_type provided.")

        if sort_by and sort_by not in ["total_amount", "total_tickets"]:
            raise HTTPException(status_code=400, detail="Invalid sort_by value.")
        
        query = (
            db.query(
                Bookings.id.label("booking_id"),
                Event.name,
                Event.event_date,
                Bookings.total_tickets,
                Bookings.total_amount,
                Bookings.status,
                Bookings.created_at,
                func.sum(BookingDetails.quantity).label("total_tickets"),
                func.sum(
                    case((BookingDetails.ticket_type.ilike("%premium%"), BookingDetails.quantity), else_=0)
                ).label("premium_tickets"),
                func.sum(
                    case((BookingDetails.ticket_type.ilike("%gold%"), BookingDetails.quantity), else_=0)
                ).label("gold_tickets"),
                func.sum(
                    case((BookingDetails.ticket_type.ilike("%silver%"), BookingDetails.quantity), else_=0)
                ).label("silver_tickets"),
                func.sum(
                    case((BookingDetails.ticket_type.ilike("%platinum%"), BookingDetails.quantity), else_=0)
                ).label("platinum_tickets"),
            )
            .join(Event, Event.id == Bookings.event_id)
            .join(BookingDetails, BookingDetails.booking_id == Bookings.id)
            .group_by(Bookings.id, Event.id)
        )

        # --- Date filter based on dropdown ---
        if start_date and end_date:
            if date_type == "booked_date":
                query = query.filter(
                    and_(
                        func.date(Bookings.created_at) >= start_date,
                        func.date(Bookings.created_at) <= end_date,
                    )
                )
            elif date_type == "event_date":
                query = query.filter(
                    and_(
                        func.date(Event.event_date) >= start_date,
                        func.date(Event.event_date) <= end_date,
                    )
                )

        # --- Search filter ---
        if search:
            query = query.filter(Event.name.ilike(f"%{search}%"))

        # --- Status filter ---
        if status:
            query = query.filter(Bookings.status == status)

        # --- Sorting ---
        if sort_by == "total_amount":
            query = query.order_by(desc(Bookings.total_amount))
        elif sort_by == "total_tickets":
            query = query.order_by(desc(Bookings.total_tickets))
        else:
            query = query.order_by(Bookings.created_at.desc())

        bookings = query.all()

        # --- Summary ---
        total_bookings = len(bookings)
        premium_tickets = sum(row.premium_tickets for row in bookings)
        gold_tickets = sum(row.gold_tickets for row in bookings)
        silver_tickets = sum(row.silver_tickets for row in bookings)
        platinum_tickets = sum(row.platinum_tickets for row in bookings)

        # --- Convert time to IST ---
        def format_ist(dt):
            if not dt:
                return None
            dt_ist = dt.replace(tzinfo=timezone.utc).astimezone(IST)
            return dt_ist.strftime("%d %b %Y, %I:%M %p")

        # --- Final Response ---
        return {
            "summary": {
                "total_bookings": total_bookings,
                "premium_tickets": premium_tickets,
                "gold_tickets": gold_tickets,
                "silver_tickets": silver_tickets,
                "platinum_tickets": platinum_tickets,
            },
            "bookings": [
                {
                    "booking_id": row.booking_id,
                    "event_name": row.name,
                    "event_date": (
                        row.event_date.strftime("%d %b %Y") if row.event_date else None
                    ),
                    "total_tickets": row.total_tickets,
                    "total_amount": row.total_amount,
                    "status": row.status.value if hasattr(row.status, "value") else row.status,
                    "Booked_at": format_ist(row.created_at),
                    "premium_tickets": row.premium_tickets,
                    "gold_tickets": row.gold_tickets,
                    "silver_tickets": row.silver_tickets,
                    "platinum_tickets": row.platinum_tickets,
                }
                for row in bookings
            ],
        }
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
            
booking_service = BookingService()