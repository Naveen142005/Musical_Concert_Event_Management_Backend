import uuid
from sqlalchemy import UUID, Column, Integer, String
from app.database.connection import Base

class Role(Base):
    __tablename__ = "role"
    
    role_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
