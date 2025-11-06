import os
import uuid
from datetime import date, datetime as dayTime, timedelta
from fastapi.encoders import jsonable_encoder
from pytest import Session
from sqlalchemy import and_, or_
from app.models.enum import EventStatus, PaymentStatus
from app.models.events import Event
from app.models.facilities import Bands, Decorations, Snacks, Venues
from app.models.facilities_selected import FacilitiesSelected, Facility_type
from app.models.payment import Payment
from app.models.tickets import Tickets
from app.schemas.event import EventBase
from app.utils.common import create_error, get_row, get_rows, update_data
from app.services.ticket import ticket_service
from app.services.facility import facility_service
from trash.venue import Venue
from sqlalchemy.orm import joinedload

class EventService:
    
    def save_image(self, event_id:int, file, db:Session):
        event_service.check_image_exist(event_id, db)

        upload_dir = "uploads/banners"
        os.makedirs(upload_dir, exist_ok=True)

       
        timestamp = dayTime.now().strftime("%Y%m%d_%H%M%S")
        extension = os.path.splitext(file.filename)[1]
        file_name = f"{timestamp}{extension}"

        file_path = os.path.join(upload_dir, file_name)

   
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        path =  file_path.replace("\\", "/")
        data = update_data(db, Event, Event.id == event_id, banner=path)
       
        db.commit()
        return path


    def check_image_exist(self, event_id, db):
        event: Event = get_row(db, Event, id=event_id)
        if event is None:
            create_error("Enter Correct Event Id")
            
        if event.banner:
            banner_path = event.banner.replace("\\", "/")
            base_dir = os.path.abspath(os.path.dirname(__file__))  
            # print (os.path.dirname(__file__))
            # print(f"base_dir = {base_dir}")
            project_root = os.path.join(base_dir, "..", "..")  
            # print(f"projecct = {project_root}")
            abs_path = os.path.join(project_root, banner_path)
            # print (type(abs_path))
            abs_path = os.path.normpath(abs_path)  
            # print("Checking path:", abs_path)

            if os.path.exists(abs_path):
                print(abs_path)
                os.remove(abs_path)
            
                
    def get_event_data_by_status(self, status: str, db: Session, userId: int = None):
     
        query = db.query(Event)
                
        if userId:
            query = query.filter(Event.user_id == userId)


        if status == "past":
            query = query.filter(or_(Event.status == EventStatus.COMPLETED, Event.status == EventStatus.CANCELLED)).order_by(Event.event_date.desc())

        elif status == "ongoing":
            query = query.filter(Event.status ==  EventStatus.ONGOING).order_by(Event.event_date.desc())

        elif status == "upcoming":
            query = query.filter(or_(Event.status == EventStatus.BOOKED, Event.status == EventStatus.RESCHEDULED)).order_by(Event.event_date.asc())
       
        elif status == "pending":
            query = (
                db.query(Event)
                .join(Payment, Event.id == Payment.event_id)
                .filter(and_(Event.user_id == userId, Payment.status == PaymentStatus.PENDING))
            )
            

        return query.all()
    
    def build_event_response(self, event_data, inserted_id: int, user_id: int, payment_id: int, total_amount:int, paid_amount: int):
        event_dict = event_data.dict()

        if not event_dict.get("ticket_enabled"):
            event_dict.pop("platinum_ticket_price", None)
            event_dict.pop("gold_ticket_price", None)
            event_dict.pop("silver_ticket_price", None)

        for facility_field in ["venue_id", "band_id", "decoration_id", "snacks_id", "snacks_count"]:
            if not event_dict.get(facility_field):
                event_dict.pop(facility_field, None)

        response = {
            "id": inserted_id,
            "user_id": user_id,
            "created_at": dayTime.utcnow().date(),
            "status": EventStatus.BOOKED,
            "payment_id": payment_id,
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            **event_dict,
        }

        if event_dict.get("payment_type") == "Half payment":
            total = event_dict.get("payment_amount", 0)
            pending = total / 2
            response["pending_amount"] = pending

        return jsonable_encoder(response)

      
    async def built_booking_response(self, data, db: Session):
        all_events = []

        for event in data:
            event_data = event.__dict__.copy()
            event_id = event.id

            event_data.pop("_sa_instance_state", None)
            
            facility_data = await facility_service.get_facility_by_event_id(event_id)
            
            
            if facility_data:
                
                total_amount_calculated = 0
                for key, value in facility_data.items():
                    if isinstance(value, dict):
                        value.pop("status", None)
                        if key == "snacks":
                            total_amount_calculated += value.get("price", 0) * value.get("count", 0)
                        else:
                            total_amount_calculated += value.get("price", 0)
                            
                if event_data["total_amount"] != total_amount_calculated:
                    event_data["pending_amount"] = total_amount_calculated - event_data["total_amount"]
                    
                event_data["facility_selected"] = facility_data
                
                
            if event.ticket_enabled:
                ticket_list = ticket_service.get_ticket_details_for_event(db, event.id)
            
                if ticket_list:
                    event_data["tickets"] = ticket_list
            else:
                event_data.pop("ticket_open_date", None)
                
            all_events.append(event_data)  
            
        return all_events
  
    async def get_my_bookings(self, userId: int, db: Session):
        current_events = get_rows(db, Event, user_id=userId)
        return await event_service.built_booking_response(current_events, db)
        
     
    async def get_bookings(self, userId: int, db: Session, status:str = None):
      
        data = event_service.get_event_data_by_status(status, db, userId)
        return await event_service.built_booking_response(data, db)
           
              
    async def get_event_by_id(self, eventId:int, db: Session):
        event = get_row(db, Event, id= eventId)
        if event is None:
            create_error("Enter Correct Event Id")
        print(event)
        return await event_service.built_booking_response([event], db)
        
 
    async def get_possible_reschedule_dates(self, eventId: int, start_date, end_date, slot, db: Session):
        
        if get_row(db, Event, id=eventId) is None:
            create_error("Provide correct event id")
        
        data = await facility_service.get_facility_by_event_id(eventId)
 
        if start_date is None or end_date is None:
             create_error("Both start_date and end_date are required")

      
        min_lead_time = date.today() + timedelta(days=1)  
        if start_date < min_lead_time:
             create_error("Start date must be at least 1 day from today")

        
        if end_date < start_date:
             create_error("End date should be after or same as the start date")
        
        max_duration = 90  
        if (end_date - start_date).days > max_duration:
             create_error(f"Event reschedule cannot exceed {max_duration} days")

        if (start_date - date.today()).days > 365:
             create_error("Start date cannot be more than 1 years from today")
    
        if (end_date - date.today()).days > 365:
            create_error("End date cannot be more than 1 years from today")
            
        facilities = ["venue", "band", "decoration"]
        unavailable_dates = {}
        available_dates = []
        
        start = dayTime.strptime(str(start_date), "%Y-%m-%d")
        end = dayTime.strptime(str(end_date), "%Y-%m-%d")
        
        current_date = start
        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")
            
            unavailable_facilities = []
            all_facilities_available = True
            
            for facility in facilities:
                if data.get(facility):
                    facility_id = data[facility]["id"]
                    facility_name = data[facility]["name"] if facility != 'snacks' else "snacks"

                    res = facility_service.check_facility_booked(db, facility_id, facility, date_str, slot, eventId)
                    if res:
                        message = f"{facility} : {facility_name} is not available"
                        unavailable_facilities.append(message)
                        all_facilities_available = False
            
            
            if unavailable_facilities:
                unavailable_dates[date_str] = unavailable_facilities
            
            
            if all_facilities_available:
                available_dates.append(date_str)
            
            current_date += timedelta(days=1)
        
        return {
            "available_dates": available_dates,
            "unavailable_dates": unavailable_dates
        }
               
    
    def get_banner(self, event_id, db):
        if event_id <= 0:
            create_error('Provide valid event Id')
        event: Event = get_row(db, Event, id=event_id)
        if event.banner:
            banner_path = event.banner.replace("\\", "/")
            base_dir = os.path.abspath(os.path.dirname(__file__))  
            # print (os.path.dirname(__file__))
            # print(f"base_dir = {base_dir}")
            project_root = os.path.join(base_dir, "..", "..")  
            # print(f"projecct = {project_root}")
            abs_path = os.path.join(project_root, banner_path)
            # print (type(abs_path))
            abs_path = os.path.normpath(abs_path)  
            # print("Checking path:", abs_path)
            return abs_path.replace("\\", "/")
        else:
            return "Please Upload banner, Then try."
        
    def calculate_total_amount(self, event_data: EventBase, db: Session):
        model = [
            (Venues, event_data.venue_id),
            (Bands, event_data.band_id),
            (Decorations, event_data.decoration_id),
            (Snacks, event_data.snacks_id)
        ]
        
        total_amount = 0
        for (name, fid) in model:
            if fid and fid != 0:
                price_amount = get_row(db, name, id = fid).price
                if (name == Snacks):
                    total_amount += price_amount * event_data.snacks_count
                else:
                    total_amount += price_amount
                
        
        return total_amount
    
    def search_public_events(
        self,
        db: Session,
        event_name: str = None,
        facility_name: str = None,
        start_date: date = None,
        end_date: date = None,
        min_price: float = None,
        max_price: float = None
    ):
        

        # Base Query
        query = (
            db.query(Event)
            .options(
                joinedload(Event.facilities)
                .joinedload(FacilitiesSelected.facility_type)
            )
            .filter(Event.ticket_enabled == True)
            .filter(Event.status.in_([EventStatus.BOOKED, EventStatus.RESCHEDULED]))
        )

        # Filters
        if event_name:
            query = query.filter(Event.name.ilike(f"%{event_name}%"))

        if start_date:
            query = query.filter(Event.event_date >= start_date)
        if end_date:
            query = query.filter(Event.event_date <= end_date)

        # Facility filter
        if facility_name:
            query = (
                query.join(FacilitiesSelected, Event.id == FacilitiesSelected.event_id)
                .join(Facility_type, FacilitiesSelected.facility_type_id == Facility_type.id)
                .filter(Facility_type.facility_type.ilike(f"%{facility_name}%"))
            )

        # Ticket price filter
        if min_price or max_price:
            query = query.join(Tickets, Event.id == Tickets.event_id)

            if min_price and max_price:
                query = query.filter(and_(Tickets.price >= min_price, Tickets.price <= max_price))
            elif min_price:
                query = query.filter(Tickets.price >= min_price)
            elif max_price:
                query = query.filter(Tickets.price <= max_price)

        events = query.distinct(Event.id).all()

        # Facility table mapping
        facility_tables = {
            "venue": Venues,
            "band": Bands,
            "decoration": Decorations,
        }

        # Build response
        result = []
        for event in events:
            # ✅ Facility details
            facility_list = []
            for f in event.facilities:
                f_type = f.facility_type.facility_type
                table = facility_tables.get(f_type)
                if table:
                    facility_detail = db.query(table).filter(table.id == f.facility_id).first()
                    if facility_detail:
                        facility_list.append({
                            "type": f_type,
                            "name": facility_detail.name,
                            "price": facility_detail.price
                        })

            # ✅ Ticket info
            tickets = db.query(Tickets).filter(Tickets.event_id == event.id).all()
            ticket_list = [
                {
                    "ticket_type_name": t.ticket_type_name,
                    "price": t.price,
                    "available_counts": t.available_counts
                }
                for t in tickets
            ]

            result.append({
                "id": event.id,
                "name": event.name,
                "slot": event.slot,
                "event_date": event.event_date,
                "ticket_open_date": event.ticket_open_date,
                "description": event.description,
                "banner": event.banner,
                "facilities": facility_list,
                "tickets": ticket_list
            })

        return result



        
event_service = EventService()  

       