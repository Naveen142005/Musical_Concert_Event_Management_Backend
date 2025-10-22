from sqlalchemy import Column, Integer, String, Date
from app.database.connection import Base


class Feedback(Base):
    __tablename__ = "feedback"
    feedback_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    feedback_rating = Column(Integer)
    feedback_summary = Column(String)
    feedback_date = Column(Date)
    status = Column(String)
