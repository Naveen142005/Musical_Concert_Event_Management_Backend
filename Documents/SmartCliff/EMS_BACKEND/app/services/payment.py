from datetime import datetime, date

from fastapi import Depends
from pytest import Session
from sqlalchemy import and_

from app.dependencies import db
from app.models.bookings import Bookings
from app.models.enum import BookingStatus, PaymentStatus
from app.models.events import Event
from app.models.refund import Refund
from app.utils.common import create_error, get_rows, insert_data, update_data
from app.models.payment import Payment as PaymentModel
class Payment:
    def calculate_refund(_,payment_amount, event_date):
    
        today = datetime.today().date()
        days_diff = (event_date - today).days

        if days_diff >= 30:
            refund_percent = 0.8  
        elif days_diff >= 15:
            refund_percent = 0.5  
        elif days_diff >= 7:
            refund_percent = 0.2  
        else:
            refund_percent = 0.0

        refund_amount = payment_amount * refund_percent
        return refund_amount
    
    def refund_to_booked_audience(self,event_id:int, reason: str,db: Session = Depends(db.get_db)):
        bookings = get_rows(db, Bookings, event_id = event_id, status = BookingStatus.BOOKED)
        bookings_ids = [(booking.id, booking.payment_id, booking.total_amount) for booking in bookings]
        
        for (bid, pid, amount) in bookings_ids:
            update_data(db, Bookings, Bookings.id == bid, status = BookingStatus.CANCELLED)
            update_data(db, PaymentModel, PaymentModel.id == pid, status = PaymentStatus.REFUND_INITIATED)
            insert_data(
            db,
            Refund,
            payment_id = pid,
            refund_reason = reason,
            refund_date = datetime.utcnow(),
            refund_amount = amount
        )
            
    def get_my_booking_payment_details(self, event_id: int, user_id: int, db: Session):
        if event_id <= 1:
            create_error("Provide proper event id")

        query = (
            db.query(Event, PaymentModel)
            .join(PaymentModel, Event.id == PaymentModel.event_id)
            .filter(
                and_(
                    Event.user_id == user_id,
                    Event.id == event_id
                )
            )
            .all()
        )

        if not query:
            create_error("No payment details found")

       
        if len(query) == 1:
            event, payment = query[0]
        else:
            completed = [item for item in query if item[1].status == PaymentStatus.COMPLETED]
            event, payment = completed[0] if completed else query[0]

        result = {
            "event_id": event.id,
            "event_name": event.name,
            "total_amount": event.total_amount,
            "payment_status": payment.status.value,
            "payment_amount": payment.payment_amount,
            "payment_mode": payment.payment_mode,
        }

       
        if payment.status == PaymentStatus.PENDING:
            result["pending_amount"] = payment.payment_amount

        return result

             
    
payment_service = Payment()
