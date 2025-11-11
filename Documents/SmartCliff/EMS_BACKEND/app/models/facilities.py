from sqlalchemy import CheckConstraint, Column, Integer, String, Float, ARRAY
from sqlalchemy.orm import relationship
from app.database.connection import Base
from app.models.enum import FacilityStatus
from sqlalchemy import Enum as SqlEnum

# ========================
#  Venues Table
# ========================
class Venues(Base):
    __tablename__ = "venues"
    __table_args__ = (
        CheckConstraint("capacity >= 0", name="check_capacity_nonnegative"),
        CheckConstraint("price >= 0", name="check_price_nonnegative"),
    )
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
    __table_args__ = (
        CheckConstraint("member_count >= 0", name="check_member_count_nonnegative"),
        CheckConstraint("price >= 0", name="check_price_nonnegative"),
    )

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
    __table_args__ = (
        CheckConstraint("price >= 0", name="check_price_nonnegative"),
    )

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
    __table_args__ = (
        CheckConstraint("price >= 0", name="check_price_nonnegative"),
    )

    id = Column(Integer, primary_key=True, index=True)
    snacks = Column(ARRAY(String))
    price = Column(Float)
    image_path = Column(String(500), nullable=True)
