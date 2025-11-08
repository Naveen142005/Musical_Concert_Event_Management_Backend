from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    feedback_rating = Column(Integer, nullable=False)
    feedback_summary = Column(String, nullable=True)
    feedback_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="submitted")
