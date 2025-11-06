import os
import uuid
from datetime import date, datetime as dayTime, timedelta
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pytest import Session
from sqlalchemy import or_
from app.models.enum import BookingStatus, EventStatus
from app.models.events import Event
from app.models.tickets import Tickets
from app.utils.common import create_error, get_row, get_rows, update_data
from app.services.ticket import ticket_service
from app.services.facility import facility_service
from app.models.bookings import BookingDetails, Bookings

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

 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
        
booking_service = BookingService()