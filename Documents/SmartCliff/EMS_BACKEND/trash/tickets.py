from sqlalchemy import Column, Integer, String
from app.database.connection import Base


class Tickets(Base):
    __tablename__ = "tickets"
    ticket_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, nullable=False)
    ticket_type = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    available_counts = Column(Integer, nullable=False)
    limit = Column(Integer)
