from sqlalchemy import DateTime, Enum as SqlEnum

import uuid
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base
from .enum import EventStatus


from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.connection import Base
from app.models.enum import ESCROWSTATUS

class Escrow(Base):
    __tablename__ = "escrow"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable= False)
    total_amount = Column(Float, nullable=False)
    released_amount = Column(Float, default=0.0)
    status = Column(SqlEnum(ESCROWSTATUS))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    event = relationship("Event", back_populates="escrow")
    # User
    user = relationship('User', back_populates="escrow")
