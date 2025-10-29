
from datetime import datetime
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from pytest import Session

from app.dependencies import db
from app.models.enum import PaymentStatus
from app.models.events import Event, EventStatusHistory
from app.models.payment import PaymentDetails, PaymentOrganizer
from app.schemas.event import EventBase
from app.services.facility import facility_service
from app.utils.common import insert_data, insert_data_flush, model_dumb
from app.services.events import event_service
from app.services.ticket import ticket_service
from app.models.enum import EventStatus

class EventCreate:
    async def create_new_event(self, event_data:EventBase,  db:Session = Depends(db.get_db)):
            
        event= insert_data_flush(
            db,
            Event,
            user_id=1,
            name=event_data.event_name,
            description=event_data.description,
            slot=event_data.slot,
            event_date=event_data.event_date,
            ticket_enabled=event_data.ticket_enabled
        )
        
        payment_details = insert_data_flush(
            db,
            PaymentDetails,
            user_id= 1,
            payment_mode=event_data.payment_mode,
            payment_date= datetime.utcnow().date(),
            payment_method= event_data.payment_type, # FUll or HALF
            status=PaymentStatus.COMPLETED
            
        )
        
        payment = insert_data_flush(
            db,
            PaymentOrganizer,
            event_id = event.id,
            payment_details_id=payment_details.id,
            payment_amount = event_data.payment_amount,
            pending_amount = 0 if event_data.payment_type == "Full payment" else event_data.payment_amount / 2
        )
        
        event.payment_id = payment.id
        
        insert_data(
            db,
            EventStatusHistory,
            event_id= event.id,
            status = EventStatus.BOOKED,
            date=datetime.utcnow()
        )
        
        inserted_id = await facility_service.add_facilities(event_data, db, event.id)
        
        if event_data.ticket_enabled:
            ticket = ticket_service.add_ticket_details(event_data, db, eventId=event.id)  
              
        db.commit()
        
        return event_service.build_event_response(event_data, event.id, user_id=1, payment_id=payment.id)
    
        
event = EventCreate()