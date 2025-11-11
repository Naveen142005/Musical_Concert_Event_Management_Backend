from datetime import datetime
from sqlalchemy import CheckConstraint, Column, Integer, String, Float, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.database.connection import Base
from app.models.enum import RefundStatus


class Refund(Base):
    __tablename__ = "refunds"
    __table_args__ = (
        CheckConstraint('refund_amount >= 0', name='check_refund_amount_nonnegative'),
    )

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey('payments.id'), nullable=False)
    refund_reason = Column(String)
    refund_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(SqlEnum(RefundStatus), default=RefundStatus.INITIATED)

    payment = relationship('Payment', back_populates='refunds')
    refund_history = relationship('RefundStatusHistory', back_populates='refund', cascade="all, delete-orphan")


class RefundStatusHistory(Base):
    __tablename__ = "refund_status_history"

    id = Column(Integer, primary_key=True, index=True)
    refund_id = Column(Integer, ForeignKey("refunds.id"), nullable=False)
    status = Column(SqlEnum(RefundStatus),  default=RefundStatus.INITIATED)
    created_at = Column(DateTime, default=datetime.utcnow)

    refund = relationship('Refund', back_populates="refund_history")  
