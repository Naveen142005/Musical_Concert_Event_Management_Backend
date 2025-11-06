from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import func
from app.models.bookings import Bookings, BookingDetails
from app.models.events import Event
from app.models.payment import Payment
from app.models.refund import Refund
from app.models.tickets import Tickets

from app.routers import booking
from app.schemas.booking import BookingCreate
from app.models.enum import BookingStatus, EventStatus, PaymentStatus
from app.utils.common import commit, create_error, get_row, get_rows, insert_data, insert_data_flush, update_data
from fastapi import HTTPException, status


class BookingCRUD:
    def create_booking(_, db: Session, booking_data: BookingCreate):
        try:
            if not get_row(db, Event, id = booking_data.event_id):
                raise HTTPException(status_code=404, message ='Event data not Found')
            
            merged_tickets = {}
            for ticket in booking_data.tickets:
                t_type = ticket.ticket_type.strip().lower()
                merged_tickets[t_type] = merged_tickets.get(t_type, 0) + ticket.quantity
            
    
            booking_data.tickets = [
                type("MergedTicket", (), {"ticket_type": t_type, "quantity": qty})
                for t_type, qty in merged_tickets.items()
            ]
            print("----------------------------------")
            print(booking_data.tickets)
            
            total_tickets = 0
            total_amount = 0
            ticket_details = []

          
            for ticket in booking_data.tickets:
               
                ticket_row = (
                    db.query(Tickets)
                    .filter(Tickets.event_id == booking_data.event_id)
                    .filter(func.lower(Tickets.ticket_type_name) == func.lower(ticket.ticket_type))
                    .first()
                )
                
                if ticket.quantity > 10:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Maximum 10 tickets allowed per booking for {ticket.ticket_type}"
                    )
                if not ticket_row:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Invalid ticket type: {ticket.ticket_type}"
                    )

                  
                if ticket_row.available_counts < ticket.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Not enough tickets available for {ticket.ticket_type}. Available: {ticket_row.available_counts}"
                    )


                if not ticket_row:
                    raise HTTPException(status_code=404, detail=f"Invalid ticket type: {ticket.ticket_type}")


                if ticket_row.available_counts < ticket.quantity:
                    raise HTTPException(status_code=400, detail=f"Not enough tickets available for {ticket.ticket_type}. Available: {ticket_row.available_counts}")


            
                subtotal = ticket_row.price * ticket.quantity
                total_tickets += ticket.quantity
                total_amount += subtotal

                ticket_details.append({
                    "ticket_type": ticket.ticket_type,
                    "quantity": ticket.quantity,
                    "subtotal": subtotal
                })

 
            booking = insert_data_flush(
                db,
                Bookings,
                user_id=booking_data.user_id,
                event_id=booking_data.event_id,
            
                booked_date=datetime.utcnow().date(),
                total_tickets=total_tickets,
                total_amount=total_amount
                
            )

            
            for td in ticket_details:
                insert_data_flush(
                    db,
                    BookingDetails,
                    booking_id=booking.id,
                    ticket_type=td["ticket_type"],
                    quantity=td["quantity"],
                    sub_total=td["subtotal"] 
                )

                db.query(Tickets).filter(
                    Tickets.event_id == booking_data.event_id,
                    func.lower(Tickets.ticket_type_name) == func.lower(td["ticket_type"])
                ).update({
                    Tickets.available_counts: Tickets.available_counts - td["quantity"],
                    Tickets.booked_ticket: Tickets.booked_ticket + td["quantity"]
                })

            payment = insert_data_flush(
                db,
                Payment,
                user_id=booking_data.user_id,
                event_id=booking_data.event_id,
                payment_amount=total_amount,
                payment_mode = booking_data.payment_mode,
                status=PaymentStatus.COMPLETED
            )
            
            booking.payment_id = payment.id

            

            commit(db)

            for td in ticket_details:
                td["ticket_type"] = td["ticket_type"].capitalize()
                
            return {
                "booking_id": booking.id,
                "user_id": booking.user_id,
                "event_id": booking.event_id,
                "tickets": ticket_details,
                "total_tickets": total_tickets,
                "total_price": total_amount,
                "status": "booked"
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Booking failed: {str(e)}")

        
    def cancel_event(self, booking_id: int, db: Session, reason: str, user_id): 
        if booking_id <= 0: 
            create_error('Provide valid event Id')
            
        data = get_row(db, Bookings, id = booking_id)
        print("_+++++++++++++++++++++++++_-")
        
        if not data:
            create_error('Provide correct Booking id, Because current Booking_id not avaiable in Db')
            
        if data.status == 'cancelled':
            create_error('Event already cancelled')
        
        updated_data = update_data(
            db,
            Bookings,
            Bookings.id == booking_id,
            status = BookingStatus.CANCELLED
        )
        
        bookings_details = get_rows(db, BookingDetails, booking_id = data.id)
        event_id = data.event_id
        

        
        for detail in bookings_details:
        # Find corresponding ticket
            ticket = (
                db.query(Tickets)
                .filter(
                    Tickets.event_id == event_id,
                    Tickets.ticket_type_name == (detail.ticket_type).capitalize()
                )
                .first()
            )

            if not ticket:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ticket type '{detail.ticket_type}' not found for this event."
                )

           
            ticket.available_counts += detail.quantity
            ticket.booked_ticket = max(ticket.booked_ticket - detail.quantity, 0)  # prevent negatives
            db.add(ticket)
            
        
        payment_data_id = get_row(db, Bookings, id = booking_id).payment_id
        
        res = ( 
               db.query(Bookings, Payment)
                .join(Payment, Bookings.payment_id == Payment.id)
                .filter(Bookings.id == booking_id).all()[0]
        )
        
        # print(res.__dict__)
        
        
        payment_updated_data = update_data (
            db,
            Payment,
            Payment.id == res.Bookings.payment_id,
            status = PaymentStatus.REFUND_INITIATED
        )
        
        event_status = get_row(db, Event, id = event_id).status
        
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(res)
        refund_amount = res.Payment.payment_amount
        if event_status == EventStatus.BOOKED: 
            refund_amount = refund_amount * 0.8
        print (refund_amount)
        insert_data(
            db,
            Refund,
            payment_id = res.Bookings.payment_id,
            refund_reason = reason,
            refund_date = datetime.utcnow(),
            refund_amount = refund_amount
        )
        
        
        
        commit(db)
        
        
        return f"{event_id } is  cancelled Successfully"
    

booking_crud = BookingCRUD()
