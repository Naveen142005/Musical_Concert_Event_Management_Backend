from sqlalchemy import Column, Integer, String
from app.database.connection import Base


class BookingsDetails(Base):
    __tablename__ = "bookings_details"
    booking_details_id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, nullable=False)
    ticket_type = Column(String)
    quantity = Column(Integer)
    sub_total = Column(Integer)
