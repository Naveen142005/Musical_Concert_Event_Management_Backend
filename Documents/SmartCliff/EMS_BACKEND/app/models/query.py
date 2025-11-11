from sqlalchemy import CheckConstraint, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base
from datetime import date

class Query(Base):
    __tablename__ = "queries"
    __table_args__ = (
        CheckConstraint("query_priority IN ('low', 'medium', 'high')", name="check_query_priority_valid"),
        CheckConstraint("status IN ('pending', 'responded', 'closed')", name="check_status_valid"),
    )
    
    query_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query_summary = Column(String, nullable=False)
    query_priority = Column(String, nullable=False)
    query_date = Column(Date, default=date.today)
    status = Column(String, default="pending")  
    admin_response = Column(String, nullable=True)