from sqlalchemy import Column, Integer
from app.database.connection import Base


class FacilitiesSelected(Base):
    __tablename__ = "facilities_selected"
    facilities_selected = Column(Integer, primary_key=True)
    event_id = Column(Integer, nullable=False)
    venue_id = Column(Integer, nullable=False)
    band_id = Column(Integer, nullable=False)
    decor_id = Column(Integer, nullable=False)
    booked_snacks_id = Column(Integer, nullable=False)
