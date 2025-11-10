from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from datetime import datetime
from app.database.connection import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    activity_type = Column(String, nullable=False)  # booking, payment, event_created, etc.
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=True)
    amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
