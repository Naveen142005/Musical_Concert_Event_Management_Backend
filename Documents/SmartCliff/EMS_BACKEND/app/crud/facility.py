from sqlalchemy.orm import Session
from fastapi import UploadFile
from pathlib import Path
import shutil
import uuid
import os
from app.models.facilities import Venues, Bands, Decorations, Snacks
from app.models.facilities_selected import FacilityUpdate
from app.utils.common import get_image_url, validate_image_file, raise_exception
from datetime import datetime


UPLOAD_DIR = Path("uploads/facilities")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Mapping facility type ID to model
FACILITY_MODEL_MAP = {
    1: Venues,
    2: Bands,
    3: Decorations,
    4: Snacks
}


class FacilityCRUD:
    
    def get_model(self, facility_type_id: int):
        model = FACILITY_MODEL_MAP.get(facility_type_id)
        if not model:
            raise ValueError("Invalid facility type")
        return model
    
    
    def get_image_url_path(self, relative_path: str):
        """Convert relative path to absolute URL"""
        if not relative_path:
            return None
        
        image = relative_path.replace("\\", "/")
        base_dir = os.path.abspath(os.path.dirname(__file__))
        project_root = os.path.join(base_dir, "..", "..")
        abs_path = os.path.join(project_root, image)
        abs_path = os.path.normpath(abs_path)
        return abs_path.replace("\\", "/")
    
    
    # CREATE
    def create_facility(self, db: Session, facility_type_id: int, data: dict):
        model = self.get_model(facility_type_id)
        new_item = model(**data)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item
    
    
    # READ
    def get_all_facilities(self, db: Session, facility_type_id: int):
        model = self.get_model(facility_type_id)
        facilities = db.query(model).all()
        
        # Add image_url to each facility
        result = []
        for facility in facilities:
            facility_dict = {
                column.name: getattr(facility, column.name) 
                for column in facility.__table__.columns
            }
            facility_dict['image_url'] = self.get_image_url_path(facility.image_path) if facility.image_path else None
            result.append(facility_dict)
        
        return result
    
    
    def get_facility_by_id(self, db: Session, facility_type_id: int, facility_id: int):
        model = self.get_model(facility_type_id)
        facility = db.query(model).filter(model.id == facility_id).first()
        
        if not facility:
            return None
        
        # Add image_url
        facility_dict = {
            column.name: getattr(facility, column.name) 
            for column in facility.__table__.columns
        }
        facility_dict['image_url'] = self.get_image_url_path(facility.image_path) if facility.image_path else None
        
        return facility_dict
    
    
    # UPDATE
    def update_facility(self, db: Session, facility_type_id: int, facility_id: int, update_data: dict):
        model = FACILITY_MODEL_MAP.get(facility_type_id)
        if not model:
            return None
        
        facility = db.query(model).filter(model.id == facility_id).first()
        if not facility:
            return None
        
        # Track only changed fields
        changed_fields = {}
        for key, new_value in update_data.items():
            if hasattr(facility, key):
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
        
        # Return facility with image_url
        facility_dict = {
            column.name: getattr(facility, column.name) 
            for column in facility.__table__.columns
        }
        facility_dict['image_url'] = self.get_image_url_path(facility.image_path) if facility.image_path else None
        
        return facility_dict
    
    
    # UPDATE IMAGE
    async def update_facility_image(self, db: Session, facility_type_id: int, facility_id: int, image: UploadFile):
        """Update facility image"""
        model = FACILITY_MODEL_MAP.get(facility_type_id)
        if not model:
            raise_exception(400, "Invalid facility type")
        
        # Check if facility exists
        facility = db.query(model).filter(model.id == facility_id).first()
        if not facility:
            raise_exception(404, "Facility not found")
        
        # Validate image
        await validate_image_file(image, max_size_mb=5)
        
        # Delete old image if exists
        if facility.image_path:
            old_image_path = Path(facility.image_path)
            if old_image_path.exists():
                old_image_path.unlink()
        
        # Save new image
        file_ext = Path(image.filename).suffix.lower()
        facility_name = model.__tablename__
        filename = f"{facility_name}_{facility_id}_{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Update database
        relative_path = f"uploads/facilities/{filename}"
        old_image = facility.image_path
        facility.image_path = relative_path
        db.commit()
        db.refresh(facility)
        
        # Log image update
        log = FacilityUpdate(
            facility_type_id=facility_type_id,
            facility_id=facility_id,
            old_value=f"image_path: {old_image}",
            new_value=f"image_path: {relative_path}",
            updated_at=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        
        return {
            "message": "Image updated successfully",
            "facility_id": facility_id,
            "image_path": relative_path,
            "image_url": self.get_image_url_path(relative_path)
        }
    
    
    # DELETE
    def delete_facility(self, db: Session, facility_type_id: int, facility_id: int):
        model = self.get_model(facility_type_id)
        facility = db.query(model).filter(model.id == facility_id).first()
        if not facility:
            return None
        
        # Delete image file if exists
        if facility.image_path:
            image_path = Path(facility.image_path)
            if image_path.exists():
                image_path.unlink()
        
        db.delete(facility)
        db.commit()
        return facility


# Create instance
facility_curd = FacilityCRUD()
