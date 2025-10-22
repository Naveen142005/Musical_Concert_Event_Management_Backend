from sqlalchemy import Column, Integer, String, Date, Boolean, LargeBinary
from app.database.connection import Base


class Events(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    banner = Column(LargeBinary)
    description = Column(String)
    slot = Column(String)
    ticket_enabled = Column(Boolean)
    status = Column(String)
    created_at = Column(Date)
    payment_id = Column(Integer)
