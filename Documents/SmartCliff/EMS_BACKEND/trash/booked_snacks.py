from sqlalchemy import Column, Integer, String, ARRAY
from app.database.connection import Base


class BookedSnacks(Base):
    __tablename__ = "booked_snacks_id"
    booked_snacks_id = Column(Integer, primary_key=True)
    snacks = Column(ARRAY(String))
    price = Column(String)
