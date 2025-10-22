from sqlalchemy import Column, Integer, String, Date
from app.database.connection import Base


class Refund(Base):
    __tablename__ = "refund"
    refund_id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, nullable=False)
    refund_reason = Column(String)
    refund_amount = Column(Integer)
    refund_date = Column(Date)
    status = Column(String)
