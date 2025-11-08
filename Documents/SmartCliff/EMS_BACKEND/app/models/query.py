from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base
from datetime import date

class Query(Base):
    __tablename__ = "queries"

    query_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query_summary = Column(String, nullable=False)
    query_priority = Column(String, nullable=False)
    query_date = Column(Date, default=date.today)
    status = Column(String, default="pending")  # pending, responded, closed
    admin_response = Column(String, nullable=True)