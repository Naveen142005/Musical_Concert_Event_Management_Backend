from sqlalchemy import Column, Integer, String, Date
from app.database.connection import Base


class EventStatusHistory(Base):
    __tablename__ = "event_status_history"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, nullable=False)
    date = Column(Date)
    status = Column(String)
