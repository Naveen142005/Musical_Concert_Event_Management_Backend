from sqlalchemy import Column, Integer, String
from app.database.connection import Base


class Decorations(Base):
    __tablename__ = "decorations"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(String)
