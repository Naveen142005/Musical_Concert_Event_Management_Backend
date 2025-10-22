from sqlalchemy import Column, Integer, Date
from app.database.connection import Base


class RecentActivity(Base):
    __tablename__ = "recent_activity"
    recent_activity_id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, nullable=False)
    added_date = Column(Date)
