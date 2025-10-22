from sqlalchemy import Column, Integer, String, Date, LargeBinary
from app.database.connection import Base


class UserDetails(Base):
    __tablename__ = "user_details"
    user_details_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    gender = Column(String)
    dob = Column(Date)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    profile_image = Column(LargeBinary)
