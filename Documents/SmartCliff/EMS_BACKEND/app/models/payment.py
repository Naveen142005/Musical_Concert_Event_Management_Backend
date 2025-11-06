from datetime import date
from sqlalchemy import Enum as SqlEnum
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
    payment_date = Column(Date, default=date.today())
    status = Column(SqlEnum(PaymentStatus))
    
    user = relationship('User', back_populates='payment')
    event = relationship(
        'Event',
        back_populates='payment',
        foreign_keys=[event_id]   # 👈 explicitly state FK to Event
    )
    refunds = relationship('Refund', back_populates='payment')
    bookings = relationship('Bookings', back_populates='payment')

from app.models.refund import Refund