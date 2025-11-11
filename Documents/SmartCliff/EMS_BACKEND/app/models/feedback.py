from datetime import datetime
from sqlalchemy import CheckConstraint, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base

class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        CheckConstraint('feedback_rating >= 1 AND feedback_rating <= 5', name='check_feedback_rating_range'),
    )
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    feedback_rating = Column(Integer, nullable=False)
    feedback_summary = Column(String, nullable=True)
    feedback_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="submitted")
