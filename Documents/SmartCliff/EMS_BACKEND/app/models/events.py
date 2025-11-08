from sqlalchemy import DateTime, Enum as SqlEnum

import uuid
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base
from .enum import EventStatus


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    banner = Column(String, default=None, nullable=True)
    description = Column(String)
    slot = Column(String)
    event_date = Column(Date)
    ticket_enabled = Column(Boolean, default=False)
    status = Column(SqlEnum(EventStatus), default=EventStatus.BOOKED)
    ticket_open_date = Column(Date, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Integer, nullable= False)
    payment_id = Column(Integer, ForeignKey("payments.id"))
    
    
    user = relationship("User", back_populates="events")
    payment = relationship(
        "Payment",
        back_populates="event",
        uselist=False,           # 👈 one payment per event
        foreign_keys="[Payment.event_id]"  # 👈 explicit FK path
    )
    status_history = relationship("EventStatusHistory", back_populates="events")
    facilities = relationship("FacilitiesSelected", back_populates="events")
    tickets = relationship('Tickets', back_populates='events')
    bookings = relationship("Bookings", back_populates="event")
 


class EventStatusHistory(Base):
    __tablename__ = "event_status_history"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    

    events = relationship("Event", back_populates="status_history")


 
from app.models.facilities_selected import FacilitiesSelected  # noqa
from app.models.payment import Payment  # noqa
from app.models.tickets import Tickets  # noqa
from app.models.bookings import Bookings  # noqa
from app.models.user import User  # noqa
