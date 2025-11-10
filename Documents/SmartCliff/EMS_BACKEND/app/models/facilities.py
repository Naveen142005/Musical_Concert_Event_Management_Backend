from sqlalchemy import Column, Integer, String, Float, ARRAY
from sqlalchemy.orm import relationship
from app.database.connection import Base
from app.models.enum import FacilityStatus
from sqlalchemy import Enum as SqlEnum


# ========================
#  Venues Table
# ========================
class Venues(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    capacity = Column(Integer)
    price = Column(Float)
    status = Column(SqlEnum(FacilityStatus), default=FacilityStatus.AVAILABLE)
    image_path = Column(String(500), nullable=True)


# ========================
#  Bands Table
# ========================
class Bands(Base):
    __tablename__ = "bands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    genre = Column(String)
    member_count = Column(Integer)
    price = Column(Float)
    status = Column(SqlEnum(FacilityStatus), default=FacilityStatus.AVAILABLE)
    image_path = Column(String(500), nullable=True)


# ========================
#  Decorations Table
# ========================
class Decorations(Base):
    __tablename__ = "decorations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String)
    price = Column(Float)
    status = Column(SqlEnum(FacilityStatus), default=FacilityStatus.AVAILABLE)
    image_path = Column(String(500), nullable=True)


# ========================
#   Snacks Table
# ========================
class Snacks(Base):
    __tablename__ = "snacks"

    id = Column(Integer, primary_key=True, index=True)
    snacks = Column(ARRAY(String))
    price = Column(Float)
    image_path = Column(String(500), nullable=True)
