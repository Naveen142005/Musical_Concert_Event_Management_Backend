from sqlalchemy import CheckConstraint, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.connection import Base



class Tickets(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint("booked_ticket >= 0", name="check_booked_ticket_nonnegative"),
        CheckConstraint("price >= 0", name="check_price_nonnegative"),
        CheckConstraint("available_counts >= 0", name="check_available_counts_nonnegative"),
        UniqueConstraint("event_id", "ticket_type_name", name="uq_event_ticket_type"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    ticket_type_name= Column(String, nullable=False)
    booked_ticket = Column(Integer, default=0)
    price = Column(Integer, nullable=False)
    available_counts = Column(Integer, nullable=False)

    events = relationship("Event", back_populates="tickets")
   