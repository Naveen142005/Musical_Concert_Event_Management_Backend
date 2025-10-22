from sqlalchemy import Column, Integer, String, ARRAY
from app.database.connection import Base


class Snacks(Base):
    __tablename__ = "snacks"
    snacks_id = Column(Integer, primary_key=True)
    price = Column(String)
    snacks = Column(ARRAY(String))
