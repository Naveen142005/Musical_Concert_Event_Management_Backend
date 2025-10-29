from sqlalchemy import Column, DateTime, Integer, String, Float, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.connection import Base



class Facility_type(Base):
    __tablename__ = 'facility_type'
    id = Column(Integer, primary_key=True, index=True)
    facility_type = Column(String, nullable=False) 
    
    facility_update = relationship('FacilityUpdate', back_populates='facility_type')
    facility_select = relationship('FacilitiesSelected', back_populates='facility_type')


class FacilitiesSelected(Base):
    __tablename__ = 'facilities_selected'
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey('events.id')) 
    facility_type_id = Column(Integer, ForeignKey('facility_type.id')) 
    facility_id = Column(Integer)
    
    facility_type = relationship('Facility_type', back_populates='facility_select')
    events = relationship('Event', back_populates='facilities')
     
     
class FacilityUpdate(Base):
    __tablename__ = "facility_updates"

    id = Column(Integer, primary_key=True, index=True)
    facility_type_id = Column(Integer, ForeignKey('facility_type.id')) 
    facility_id = Column(Integer)
    old_value = Column(String)
    new_value = Column(String)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    facility_type = relationship('Facility_type', back_populates='facility_update')
    


    
  