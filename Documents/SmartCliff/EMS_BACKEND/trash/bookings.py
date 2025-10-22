from sqlalchemy import Column, Integer, String, Date, Boolean
from app.database.connection import Base


class Bookings(Base):
    __tablename__ = "bookings"
    booking_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    event_id = Column(Integer, nullable=False)
    booked_date = Column(Date)
    total_tickets = Column(Integer)
    total_amount = Column(Integer)
    status = Column(String)
