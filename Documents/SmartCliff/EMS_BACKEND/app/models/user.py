import uuid
from sqlalchemy import UUID, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, Date, Boolean
from app.database.connection import Base
from datetime import date, datetime
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint("length(email) > 0", name="check_email_not_empty"),
        CheckConstraint("length(password) > 6", name="check_password_min_length"),
    )
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    role_id = Column(Integer, ForeignKey("role.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(Integer)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Boolean, default=True)

    role = relationship("Role", back_populates="user")
    user_detail = relationship('UserDetails', back_populates='user')
    events = relationship('Event', back_populates='user')
    bookings = relationship("Bookings", back_populates="user")
    payment = relationship("Payment", back_populates='user')
    escrow = relationship('Escrow', back_populates='user')

class UserDetails(Base):
    __tablename__ = "user_details"
    __table_args__ = (
        CheckConstraint("dob IS NULL OR dob <= CURRENT_DATE", name="check_dob_past_or_null"),
    )
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"),nullable=False)
    gender = Column(String)
    dob = Column(Date)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    profile_image = Column(String)
    
    user = relationship('User', back_populates='user_detail')
    
    
