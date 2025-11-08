
from datetime import date, datetime 
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pytest import Session
from sqlalchemy import and_, null

from app.dependencies import db
from app.models.enum import FacilityStatus, PaymentMode, PaymentStatus
from app.models.events import Event, EventStatusHistory
from app.models.facilities import Bands, Decorations, Venues
from app.models.facilities_selected import FacilitiesSelected

from app.models.payment import Payment, PaymentStatusHistory
from app.models.refund import Refund, RefundStatusHistory
from app.models.tickets import Tickets
from app.schemas.event import EventBase
from app.services.facility import facility_service
from app.utils.common import commit, create_error, delete_data, get_row, get_rows, insert_data, insert_data_flush, model_dumb, update_data
from app.services.events import event_service
from app.services.ticket import ticket_service
from app.services.payment import payment_service
from app.models.enum import EventStatus

class EventCRUD:
    async def create_new_event(self, event_data:EventBase,  db:Session = Depends(db.get_db)):
        event_date = event_data.event_date
        slot = event_data.slot

        
        checks = [
            ("venue", event_data.venue_id),
            ("band", event_data.band_id),
            ("decoration", event_data.decoration_id)
           
        ]
        
        facilities = {
            "Venue": (Venues, event_data.venue_id),
            "Band": (Bands, event_data.band_id),
            "Decoration": (Decorations, event_data.decoration_id),
       
        }

        for name, (model, fid) in facilities.items():
            if fid:
                facility = db.query(model).filter(model.id == fid).first()
                if not facility:
                    raise HTTPException(
                        status_code=404,
                        detail=f"{name} with ID {fid} does not exist."
                    )
                if facility.status and facility.status != FacilityStatus.AVAILABLE:
                    raise HTTPException(
                        status_code=400,
                        detail=f"{name} with ID {fid} is not available (status: {facility.status.value})."
                    )
        

        for name, fid in checks:
            if fid and fid != 0:
                res = facility_service.check_avaiable(db, fid, name, event_data.event_date, event_data.slot)
                # print(res, name, fid)
                if res:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"{name} id_{fid} already booked for {event_data.event_date} {event_data.slot}")
                
        total_amount = event_service.calculate_total_amount(event_data, db)
        
        isFullPayment = False
        if event_data.payment_type == "Full Payment": isFullPayment = True
        
        paying_amount =  total_amount if isFullPayment else total_amount / 2
        
        event= insert_data_flush(
            db,
            Event,
            user_id=7,
            name=event_data.event_name,
            description=event_data.description,
            slot=event_data.slot,
            event_date=event_data.event_date,
            ticket_enabled=event_data.ticket_enabled,
            ticket_open_date= event_data.ticket_open_date,
            total_amount = paying_amount
        )
        
        # print("=================++++++++++++++++++++++")

        
        
        payment = insert_data_flush(
            db,
            Payment,
            user_id = 1,
            event_id = event.id,
            payment_amount = paying_amount,
            payment_mode = event_data.payment_mode,
            status = PaymentStatus.COMPLETED if isFullPayment else PaymentStatus.PENDING
        )
        
        event.payment_id = payment.id
        
        insert_data(
            db,
            EventStatusHistory,
            event_id= event.id,
            status = EventStatus.BOOKED
            
        )
        
        insert_data(
            db,
            PaymentStatusHistory,
            payment_id = payment.id,
            status = PaymentStatus.COMPLETED if isFullPayment else PaymentStatus.PENDING
        )
        
        inserted_id = await facility_service.add_facilities(event_data, db, event.id)
        
        if event_data.ticket_enabled:
            ticket = ticket_service.add_ticket_details(event_data, db, eventId=event.id)  
              
        commit(db)
        
        return event_service.build_event_response(event_data, event.id, user_id=1, payment_id=payment.id, total_amount= total_amount, paid_amount=paying_amount)
    
    async def reshedule_event(self,event_id: int, reshedule_date, ticket_opening_date, slot:str ,db: Session):
        
        if event_id <= 0:
            create_error('Provide valid event Id')
            
        data:Event = get_row(db, Event, id= event_id)
        
        if data.status != EventStatus.BOOKED:
            create_error(f'The event which is already {str(data.status)[12:].lower()} can not be reshedule')
        
        if not data:
            create_error('Provide correct event id, Because current event_id not avaiable in Db')
            
        dates = await event_service.get_possible_reschedule_dates(event_id, reshedule_date, reshedule_date,slot, db)
       
        
        available_dates = [date.fromisoformat(d) for d in dates["available_dates"]]
        
        if reshedule_date not in available_dates:
            create_error(f'Can not reschedule at the {reshedule_date}')
            
        
        if reshedule_date <= ticket_opening_date:
            create_error(f'Ticket opening date should be before the resheduling_date.')
        
        updated_data = update_data(
            db, 
            Event, 
            Event.id == event_id, 
            ticket_open_date = ticket_opening_date,
            event_date = reshedule_date, 
            slot= slot,
            status = EventStatus.RESCHEDULED)
        
        insert_data(
            db, 
            EventStatusHistory, 
            event_id= event_id,
            status = EventStatus.RESCHEDULED
        )
        
        commit(db)
        
        return {"Updated_data": updated_data, "mes": "Success"}
        
    def cancel_event(self, event_id: int, db: Session, reason: str, user_id: int): 
        if event_id <= 0:
            create_error('Provide valid event Id')
        data = get_row(db, Event, id= event_id)
        if not data:
            create_error('Provide correct event id, Because current event_id not avaiable in Db')
        
        if data.status == 'cancelled':
            create_error('Event already cancelled')
        
        updated_data = update_data(
            db,
            Event,
            Event.id == event_id,
            status = EventStatus.CANCELLED
        )
         
        insert_data(
            db, 
            EventStatusHistory, 
            event_id= event_id,
            status = EventStatus.CANCELLED
        )
        
        payment_data: Payment = get_row(db, Payment, event_id = event_id, user_id = user_id)
        
        payment_updated_data = update_data (
            db,
            Payment,
            Payment.id == payment_data.id,
            status = PaymentStatus.REFUND_INITIATED
        )
        
        insert_data(
            db,
            PaymentStatusHistory,
            payment_id = payment_data.id,
            status = PaymentStatus.REFUND_INITIATED
        )
        
        event_date = get_row(db, Event, id = event_id).event_date
        
        refund_amount = payment_service.calculate_refund(payment_data.payment_amount,event_date)
        
      
        refund_data = insert_data_flush(
            db,
            Refund,
            payment_id = payment_data.id,
            refund_reason = reason,
            refund_amount = refund_amount
        )
        
        insert_data(
            db,
            RefundStatusHistory,
            refund_id = refund_data.id,
        )
        
        payment_service.refund_to_booked_audience(event_id, "Cancelled by the booked Organizer:" + reason,db)
        
        commit(db)
        
        
        # Should give refund to all the booked audience. (DONE)
        
        return f"{event_id } is  cancelled Successfully"
    
    def pay_pending_amount(self, event_id: int, user_id: int, payment_mode, db: Session):
        query = (
            db.query(Event, Payment)
            .join(Payment, Event.id == Payment.event_id)
            .filter(
                and_(Payment.status == PaymentStatus.PENDING, Payment.user_id == user_id, event_id == Payment.event_id)
            )
        ).all()
        print(len(query))
        
        if not query:
            raise HTTPException(status_code=404, detail="Full Payment already paids")
        
        update_data(db, Event, Event.id == event_id, total_amount = Event.total_amount * 2)   
        
        query = query[0]
        
        db.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.event_id == event_id
        ).update({
            Payment.payment_amount: Payment.payment_amount * 2,
            Payment.payment_mode: payment_mode.value,
            Payment.status: PaymentStatus.COMPLETED
        })
        
        payment_data = db.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.event_id == event_id
        ).first()
        
        insert_data(
            db,
            PaymentStatusHistory,
            payment_id = payment_data.id,
            status = PaymentStatus.COMPLETED
        )
        
        commit(db)
        
        return "SUCCESS"
    
event = EventCRUD()
event_crud = EventCRUD()