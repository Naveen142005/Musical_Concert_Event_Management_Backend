from sqlalchemy import Column, Integer
from app.database.connection import Base


class PaymentAudience(Base):
    __tablename__ = "payment(audience)"
    payment_id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, nullable=False)
    payment_details_id = Column(Integer, nullable=False)
