from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database.connection import Base
from app.models.enum import PaymentStatus, RefundStatus


# ------------------- Payment Details -------------------
class PaymentDetails(Base):
    __tablename__ = "payment_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    payment_method = Column(String, nullable=False)
    payment_mode = Column(String, nullable=False)
    payment_date = Column(Date, nullable=False)
    status = Column(SqlEnum(PaymentStatus), default=PaymentStatus.PENDING)

    # relationships
    organizer_payments = relationship("PaymentOrganizer", back_populates="payment_details")
    audience_payments = relationship("PaymentAudience", back_populates="payment_details")


# ------------------- Payment (Organizer) -------------------
class PaymentOrganizer(Base):
    __tablename__ = "payment_organizer"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, nullable=False)
    payment_details_id = Column(Integer, ForeignKey("payment_details.id"))
    payment_amount = Column(Float, nullable=False)
    pending_amount = Column(Float)

    # relationships
    payment_details = relationship("PaymentDetails", back_populates="organizer_payments")
    refunds = relationship("RefundOrganizer", back_populates="organizer_payment")
    events = relationship("Event", back_populates="payment")


# ------------------- Payment (Audience) -------------------
class PaymentAudience(Base):
    __tablename__ = "payment_audience"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, nullable=False)
    payment_details_id = Column(Integer, ForeignKey("payment_details.id"))
    payment_amount = Column(Float, nullable=False)

    # relationships
    payment_details = relationship("PaymentDetails", back_populates="audience_payments")
    refunds = relationship("RefundAudience", back_populates="audience_payment")


# ------------------- Refund (Organizer) -------------------
class RefundOrganizer(Base):
    __tablename__ = "refund_organizer"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payment_organizer.id"))
    refund_reason = Column(String, nullable=False)
    refund_amount = Column(Float, nullable=False)
    refund_date = Column(Date, nullable=False)
    status = Column(SqlEnum(RefundStatus), default=RefundStatus.INITIATED)

    # relationship
    organizer_payment = relationship("PaymentOrganizer", back_populates="refunds")


# ------------------- Refund (Audience) -------------------
class RefundAudience(Base):
    __tablename__ = "refund_audience"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payment_audience.id"))
    refund_reason = Column(String, nullable=False)
    refund_amount = Column(Float, nullable=False)
    refund_date = Column(Date, nullable=False)
    status = Column(SqlEnum(RefundStatus), default=RefundStatus.INITIATED)

    # relationship
    audience_payment = relationship("PaymentAudience", back_populates="refunds")
