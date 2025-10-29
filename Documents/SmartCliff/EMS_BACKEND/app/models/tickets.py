from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base



class Tickets(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    ticket_type_name= Column(String, nullable=False)
    booked_ticket = Column(Integer, default=0)
    price = Column(Integer, nullable=False)
    available_counts = Column(Integer, nullable=False)

    events = relationship("Event", back_populates="tickets")
   