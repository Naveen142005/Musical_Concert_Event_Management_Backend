from sqlalchemy import Column, Integer, String
from app.database.connection import Base


class Venue(Base):
    __tablename__ = "venue"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(String)
