from datetime import datetime, date, timezone

from fastapi import Depends
from pytest import Session
from sqlalchemy import and_, func, or_

from app.dependencies import db
from app.models.bookings import Bookings
from app.models.enum import BookingStatus, PaymentStatus
from app.models.events import Event
from app.models.refund import Refund, RefundStatusHistory
from app.models.role import Role
from app.models.user import User
from app.utils.common import create_error, format_ist, get_rows, insert_data, insert_data_flush, update_data
from app.models.payment import Payment as PaymentModel, PaymentStatusHistory
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
            refund_percent = 0.1

        refund_amount = payment_amount * refund_percent
        return refund_amount
    
    def refund_to_booked_audience(self,event_id:int, reason: str,db: Session = Depends(db.get_db)):
        bookings = get_rows(db, Bookings, event_id = event_id, status = BookingStatus.BOOKED)
        if not bookings: 
            return
        bookings_ids = [(booking.id, booking.payment_id, booking.total_amount) for booking in bookings]
        
        for (bid, pid, amount) in bookings_ids:
            
            update_data(db, Bookings, Bookings.id == bid, status = BookingStatus.CANCELLED)
            update_data(db, PaymentModel, PaymentModel.id == pid, status = PaymentStatus.REFUND_INITIATED)
            
            refund_data = insert_data_flush(
            db,
            Refund,
            payment_id = pid,
            refund_reason = reason,
            refund_amount = amount
        )
            insert_data(
            db,
            PaymentStatusHistory,
            payment_id = pid,
            status = PaymentStatus.REFUND_INITIATED
        )
            insert_data(
            db,
            RefundStatusHistory,
            refund_id = refund_data.id
        )
    
    
    def get_all_payments(
        self,
        db: Session,
        start_date=None,
        end_date=None,
        search=None,
        status=None,
        role=None
    ):
        query = (
            db.query(
                User.name.label("customer_name"),
                Role.name.label("role_name"),
                Event.name.label("event_name"),
                PaymentModel.created_at.label("payment_date"),
                PaymentModel.payment_mode.label("payment_method"),
                PaymentModel.payment_amount.label("amount_paid"),
                PaymentModel.status.label("status"),
                Event.id.label("event_id"),
            )
            .join(Role, Role.id == User.role_id)
            .join(PaymentModel, PaymentModel.user_id == User.id)
            .join(Event, Event.id == PaymentModel.event_id)
        )

        if start_date and end_date:
            query = query.filter(
                and_(
                    func.date(PaymentModel.created_at) >= start_date,
                    func.date(PaymentModel.created_at) <= end_date,
                )
            )

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    User.name.ilike(search_pattern),
                    Event.name.ilike(search_pattern),
                )
            )

        if status:
            query = query.filter(PaymentModel.status == status)

        if role:
            query = query.filter(Role.name.ilike(role))

        query = query.order_by(PaymentModel.created_at.desc())
        records = query.all()



        result = []
        for row in records:
            pending_amount = (
                0
                if row.status == PaymentStatus.COMPLETED
                else row.amount_paid
            )

            result.append(
                {
                    "role": row.role_name.capitalize(),
                    "customer_name": row.customer_name,
                    "event_name": row.event_name,
                    "payment_date": format_ist(row.payment_date),
                    "payment_method": row.payment_method,
                    "amount_paid": row.amount_paid,
                    "pending": pending_amount,
                    "status": row.status.value if hasattr(row.status, "value") else row.status,
                }
            )

        total_revenue = sum(row.amount_paid for row in records)
        completed_count = sum(1 for row in records if row.status == PaymentStatus.COMPLETED)
        pending_count = sum(1 for row in records if row.status == PaymentStatus.PENDING)
        failed_count = sum(1 for row in records if row.status == PaymentStatus.FAILED)

        summary = {
            "total_revenue": total_revenue,
            "completed": completed_count,
            "pending": pending_count,
            "failed": failed_count,
        }

        return {"summary": summary, "payments": result}
    
    
    
payment_service = Payment()
