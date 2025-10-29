from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.facilities import Venues, Bands, Decorations, Snacks
from datetime import datetime
from sqlalchemy.orm import Session
from app.dependencies import db
from app.models.events import Event
from app.models.facilities import Decorations, Snacks, Venues, Bands
from app.models.facilities_selected import FacilitiesSelected, Facility_type
from app.database.connection_mongo import col
from app.schemas.event import EventBase
from app.utils.common import get_row, insert_data_flush, model_dumb


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
                
                added_facility = insert_data_flush(
                    db, 
                    FacilitiesSelected, 
                    event_id = eventId,
                    facility_type_id= facility_type.id,
                    facility_id = id
                )
            
        facility_inserted = await col.insert_one(data)
        return str(facility_inserted.inserted_id)
       

        
facility_service = FacilityService()