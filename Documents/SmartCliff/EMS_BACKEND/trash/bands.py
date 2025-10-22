from sqlalchemy import Column, Integer, String
from app.database.connection import Base


class Bands(Base):
    __tablename__ = "bands"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    capacity = Column(Integer)
    member_count = Column(Integer)
    status = Column(String)
    price = Column(Integer)
