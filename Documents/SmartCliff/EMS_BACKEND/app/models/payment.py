from datetime import date, datetime
from sqlalchemy import DateTime, Enum as SqlEnum
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database.connection import Base
from app.models.enum import PaymentStatus, RefundStatus


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index= True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id'), nullable = False)
    payment_mode = Column(String)
    payment_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(SqlEnum(PaymentStatus))
    
    user = relationship('User', back_populates='payment')
    event = relationship(
        'Event',
        back_populates='payment',
        foreign_keys=[event_id]   # 👈 explicitly state FK to Event
    )
    refunds = relationship('Refund', back_populates='payment')
    bookings = relationship('Bookings', back_populates='payment')
    payment_history = relationship('PaymentStatusHistory', back_populates='payment', cascade="all, delete-orphan")


class PaymentStatusHistory(Base):
    __tablename__ = "payment_status_history"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    status = Column(SqlEnum(PaymentStatus))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    payment = relationship('Payment', back_populates="payment_history")
    

from app.models.refund import Refund