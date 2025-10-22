from sqlalchemy import Column, Integer, String, Date
from app.database.connection import Base


class PaymentDetails(Base):
    __tablename__ = "payment_details"
    payment_details_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    payment_method = Column(String)
    payment_date = Column(Date)
    status = Column(String)
