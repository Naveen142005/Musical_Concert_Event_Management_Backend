from sqlalchemy import Column, Integer, String, Float, ARRAY, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.database.connection import Base
from app.models.enum import FacilityStatus


# ========================
#  Venue Table
# ========================
class Venues(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    capacity = Column(Integer)
    price = Column(Float)
    status = Column(SqlEnum(FacilityStatus), default=FacilityStatus.AVAILABLE)


# ========================
#  Bands Table
# ========================
class Bands(Base):
    __tablename__ = "bands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    genre = Column(String)
    capacity = Column(Integer)
    member_count = Column(Integer)
    price = Column(Float)
    status = Column(SqlEnum(FacilityStatus), default=FacilityStatus.AVAILABLE)


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


# ========================
#  Booked Snacks Table
# ========================
class Snacks(Base):
    __tablename__ = "booked_snacks"

    id = Column(Integer, primary_key=True, index=True)
    snacks = Column(ARRAY(String))
    price = Column(Float)
