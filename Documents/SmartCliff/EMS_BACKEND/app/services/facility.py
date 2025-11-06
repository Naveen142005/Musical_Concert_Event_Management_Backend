from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date as DateType, timedelta
from app.models.enum import EventStatus
from app.models.facilities import Venues, Bands, Decorations, Snacks
from datetime import datetime
from sqlalchemy.orm import Session
from app.dependencies import db
from app.models.events import Event
from app.models.facilities import Decorations, Snacks, Venues, Bands
from app.models.facilities_selected import FacilitiesSelected, Facility_type
from app.database.connection_mongo import col
from app.schemas.event import EventBase
from app.utils.common import create_error, get_row, insert_data, insert_data_flush, model_dumb


class FacilityGettingService:
   
    def get_venues(self, db: Session, model_dict: dict):
        query = db.query(Venues)

        if model_dict.get("name"):
            query = query.filter(Venues.name.ilike(f"%{model_dict['name']}%"))

        if model_dict.get("location"):
            query = query.filter(Venues.location.ilike(f"%{model_dict['location']}%"))

        if model_dict.get("min_capacity"):
            query = query.filter(Venues.capacity >= model_dict["min_capacity"])

        if model_dict.get("max_price"):
            query = query.filter(Venues.price <= model_dict["max_price"])

        
         
        sort_by = model_dict.get("sort_by", "name")
        order = model_dict.get("order", "asc")

        if sort_by and hasattr(Venues, sort_by):
            column = getattr(Venues, sort_by)
            query = query.order_by(column.desc() if order == "desc" else column.asc())

        return query.all()


   
    def get_bands(self, db: Session, model_dict: dict):
        query =  db.query(Bands)


        if model_dict.get("name"):
            query = query.filter(Bands.name.ilike(f"%{model_dict['name']}%"))

        if model_dict.get("genre"):
            query = query.filter(Bands.genre.ilike(f"%{model_dict['genre']}%"))

        if model_dict.get("member_count"):
            query = query.filter(Bands.member_count == model_dict["member_count"])
        
        query.filter([])

        if model_dict.get("max_price"):
            query = query.filter(Bands.price <= model_dict["max_price"])

        sort_by = model_dict.get("sort_by", "name")
        order = model_dict.get("order", "asc")

        if sort_by and hasattr(Bands, sort_by):
            column = getattr(Bands, sort_by)
            query = query.order_by(column.desc() if order == "desc" else column.asc())

        return query.all()


    
    def get_decorations(self, db: Session, model_dict: dict):
        query = db.query(Decorations)

        if model_dict.get("name"):
            query = query.filter(Decorations.name.ilike(f"%{model_dict['name']}%"))

        if model_dict.get("type"):
            query = query.filter(Decorations.type.ilike(f"%{model_dict['type']}%"))

        if model_dict.get("max_price"):
            query = query.filter(Decorations.price <= model_dict["max_price"])

        sort_by = model_dict.get("sort_by", "name")
        order = model_dict.get("order", "asc")

        if sort_by and hasattr(Decorations, sort_by):
            column = getattr(Decorations, sort_by)
            query = query.order_by(column.desc() if order == "desc" else column.asc())

        return query.all()


  
    def get_snacks(self, db: Session, model_dict: dict):
        query = db.query(Snacks)
        

        if model_dict.get("price"):
            query = query.filter(Snacks.price <= model_dict["price"])

        sort_by = model_dict.get("sort_by", "id")
        order = model_dict.get("order", "asc")

        if sort_by and hasattr(Snacks, sort_by):
            column = getattr(Snacks, sort_by)
            query = query.order_by(column.desc() if order == "desc" else column.asc())

        return query.all()

class FacilityService:
    async def add_facilities(self, event_data: EventBase, db: Session, eventId):
        data = {
            "event_id": eventId
        }
        
        facility_model = {
            "venue" : (Venues, event_data.venue_id),
            "band": (Bands, event_data.band_id),
            "decoration": (Decorations, event_data.decoration_id),
            "snacks": (Snacks, event_data.snacks_id)
        }
        
        
        for key, (model, id) in facility_model.items():
            if id:
                facility = get_row(db, model, id = id)
                data[key] = model_dumb(facility)
                facility_type = get_row(db, Facility_type, facility_type = key)
                
                added_facility = insert_data(
                    db, 
                    FacilitiesSelected, 
                    event_id = eventId,
                    facility_type_id= facility_type.id,
                    facility_id = id
                )
        if not data.get('snacks'):
            data['snacks'] = {}

        data['snacks']['count'] = event_data.snacks_count
        facility_inserted = await col.insert_one(data)
        return str(facility_inserted.inserted_id)
       
    def check_avaiable(self, db:Session, facility_id: int ,facility_name: str, date: DateType, slot: str, bool = True):
        
        facility_model = {
            "venue" : (Venues, facility_id),
            "band": (Bands, facility_id),
            "decoration": (Decorations, facility_id),
        }
        if bool:
            if not facility_model[facility_name]:
                create_error('Enter Correct facility name as mentioned')
            
            model_class, fid = facility_model[facility_name]

            if not get_row(db, model_class, id = fid):
                create_error(f"Enter Correct {facility_name}'s Id")
                
            
            if date <= date.today(): 
                create_error("Expected date should after the today's date.")
        
        
        res = (
            db.query(FacilitiesSelected)
            .join(Facility_type,  )
            .join(Event, Event.id == FacilitiesSelected.event_id)
            .filter(
                and_(
                    Facility_type.facility_type == facility_name,
                    Event.event_date == date,   
                    FacilitiesSelected.facility_id == facility_id,
                    Event.status.in_([EventStatus.BOOKED, EventStatus.RESCHEDULED])
                )
            ).first()
        )
        
        return res
    
    def check_facility_booked(self, db:Session, facility_id: int ,facility_name: str, date: DateType, slot: str, event_id:int):
        res = (
            db.query(FacilitiesSelected)
            .join(Facility_type, FacilitiesSelected.facility_type_id == Facility_type.id)
            .join(Event, Event.id == FacilitiesSelected.event_id)
            .filter(
                and_(
                    Facility_type.facility_type == facility_name,
                    Event.event_date == date,
                    FacilitiesSelected.facility_id == facility_id,
                    Event.slot == slot,
                    Event.id != event_id,
                    Event.status.in_([EventStatus.BOOKED, EventStatus.RESCHEDULED])
                )
            ).first()   
        )
        
        return res
    
    async def get_facility_by_event_id(self, event_id: int):
        facility = await col.find_one({"event_id": event_id}, {"_id": 0})  
        return facility if facility else None
    
       
    def get_facilities_available_dates(self ,slot, venue_id, band_id, decoration_id, no_days, db:Session):
        
        model_dict = [("venue", venue_id) , ("band", band_id), ("decoration", decoration_id)]
        
        if venue_id:
            if get_row(db, Venues, id=venue_id) is None or venue_id <= 0:
                create_error('Enter Correct Venue id')
            
        if band_id:
            if get_row(db, Bands, id=band_id) is None or band_id <= 0:
                create_error('Enter Correct Band id')
            
        if decoration_id :
            if get_row(db, Decorations, id=decoration_id) is None or decoration_id <=     0:
                create_error('Enter Correct Decorations id')    
        
        if no_days >= 101:
            create_error('No of days can not exceed 100')
            
        date_str = datetime.now().date()
        all_available_dates = []
        print(date_str)
        while no_days != 0:
            no_days -= 1
            all_available = True
            for (key, value) in model_dict:
                if value:
                    res = facility_service.check_avaiable(db, value, key, date_str, slot, False)
                    if res: 
                        all_available = False
                        break
            if all_available:
                all_available_dates.append(date_str.strftime("%Y-%m-%d"))
            date_str += timedelta(days=1)
                        
        return all_available_dates  
  
        
        
facility_service = FacilityService()


