from sqlalchemy.orm import Session
from app.models.facilities import Venues, Bands, Decorations, Snacks
from app.models.facilities_selected import FacilityUpdate
from datetime import datetime

# Mapping facility type ID to model
FACILITY_MODEL_MAP = {
    1: Venues,
    2: Bands,
    3: Decorations,
    4: Snacks
}


def get_model(facility_type_id: int):
    model = FACILITY_MODEL_MAP.get(facility_type_id)
    if not model:
        raise ValueError("Invalid facility type")
    return model


# CREATE
def create_facility(db: Session, facility_type_id: int, data: dict):
    model = get_model(facility_type_id)
    new_item = model(**data)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


# READ
def get_all_facilities(db: Session, facility_type_id: int):
    model = get_model(facility_type_id)
    return db.query(model).all()


def get_facility_by_id(db: Session, facility_type_id: int, facility_id: int):
    model = get_model(facility_type_id)
    return db.query(model).filter(model.id == facility_id).first()




FACILITY_MAP = {
    1: Venues,
    2: Bands,
    3: Decorations,
    4: Snacks,
}


def update_facility(db: Session, facility_type_id: int, facility_id: int, update_data: dict):
    model = FACILITY_MAP.get(facility_type_id)
    if not model:
        return None

    facility = db.query(model).filter(model.id == facility_id).first()
    if not facility:
        return None

    # Track only changed fields
    changed_fields = {}
    for key, new_value in update_data.items():
        old_value = getattr(facility, key)
        if old_value != new_value:
            changed_fields[key] = {"old": old_value, "new": new_value}
            setattr(facility, key, new_value)

    # Commit facility update
    db.commit()
    db.refresh(facility)

    # Log changes in FacilityUpdate table
    for key, change in changed_fields.items():
        log = FacilityUpdate(
            facility_type_id=facility_type_id,
            facility_id=facility_id,
            old_value=f"{key}: {change['old']}",
            new_value=f"{key}: {change['new']}",
            updated_at=datetime.utcnow()
        )
        db.add(log)

    db.commit()
    return facility


# DELETE
def delete_facility(db: Session, facility_type_id: int, facility_id: int):
    model = get_model(facility_type_id)
    facility = db.query(model).filter(model.id == facility_id).first()
    if not facility:
        return None
    db.delete(facility)
    db.commit()
    return facility
