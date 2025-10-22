from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Date, Boolean
from app.database.connection import Base
from datetime import date

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.role_id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(Integer)
    password = Column(String, nullable=False)
    created_at = Column(Date, default=date.today)
    status = Column(Boolean, default=True)
