from sqlalchemy import Column, Integer, String, Date
from app.database.connection import Base


class Queries(Base):
    __tablename__ = "queries"
    query_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    query_summary = Column(String)
    query_priority = Column(String)
    query_date = Column(Date)
    status = Column(String)
