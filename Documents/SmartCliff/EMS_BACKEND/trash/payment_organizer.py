from sqlalchemy import Column, Integer
from app.database.connection import Base


class PaymentOrganizer(Base):
    __tablename__ = "payment(organizer)"
    payment_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, nullable=False)
    payment_details_id = Column(Integer, nullable=False)
