import uuid
from sqlalchemy import UUID, Column, Integer, String
from app.database.connection import Base
from sqlalchemy.orm import relationship
class Role(Base):
    __tablename__ = "role"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    user = relationship('User', back_populates='role')