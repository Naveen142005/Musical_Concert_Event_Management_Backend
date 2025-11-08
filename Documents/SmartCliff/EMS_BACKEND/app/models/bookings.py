from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SqlEnum

from app.models.enum import BookingStatus
from app.database.connection import Base


class Bookings(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    total_tickets = Column(Integer, nullable=False)
    total_amount = Column(Integer, nullable=False)
    status = Column(SqlEnum(BookingStatus), default=BookingStatus.BOOKED, nullable=False)

    user = relationship("User", back_populates="bookings")
    event = relationship("Event", back_populates="bookings")
    booking_details = relationship("BookingDetails", back_populates="booking")
    payment = relationship("Payment", back_populates="bookings")


class BookingDetails(Base):
    __tablename__ = "booking_ticket_details"

    booking_details_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    ticket_type = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    sub_total = Column(Integer, nullable=False)

    booking = relationship("Bookings", back_populates="booking_details")
    

from app.models.enum import BookingStatus
from app.models.user import User  # noqa
from app.models.events import Event  # noqa