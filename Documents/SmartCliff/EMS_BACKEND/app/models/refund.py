from datetime import date
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database.connection import Base
from app.models.enum import PaymentStatus, RefundStatus



class Refund(Base):
    __tablename__ = "refunds"
    
    id = Column(Integer, primary_key=True, index= True)
    payment_id = Column(Integer, ForeignKey('payments.id'), nullable=False)
    refund_reason = Column(String)
    refund_amount = Column(Float)
    refund_date = Column(Date, default=date.today())
    status = Column(SqlEnum(RefundStatus), default=RefundStatus.INITIATED)
    
    payment = relationship('Payment', back_populates='refunds')
