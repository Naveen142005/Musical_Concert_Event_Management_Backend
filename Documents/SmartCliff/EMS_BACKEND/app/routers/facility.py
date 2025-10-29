from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.models.enum import SortOrder
from app.services import facility
from app.dependencies import db

router = APIRouter(prefix="/facilities")
service = facility.FacilityGettingService()


@router.get("/venues")
def get_all_venues(
    name: str | None = Query(None, description="Show venues only by the Names."),
    location: str | None = Query(None, description="Show venues only from this location (can match partly)."),
    min_capacity: int | None = Query(None, description="Show venues with at least this much capacity."),
    max_price: float | None = Query(None, description="Show only items with price less than or equal to this value."),
    sort_by: str | None = Query(None, description="Sort by this column name (like price, name, or capacity)."),
    order: SortOrder = Query(SortOrder.asc, description="Sort order — 'asc' for ascending, 'desc' for descending."),
    db: Session = Depends(db.get_db)
):
    model_dict = {
        "name": name,
        "location": location,
        "min_capacity": min_capacity,
        "max_price": max_price,
        "sort_by": sort_by,
        "order": order
    }
    return service.get_venues(db, model_dict)


@router.get("/bands")
def get_all_bands(
    name: str | None = Query(None, description="Filter bands by name."),
    genre: str | None = Query(None, description="Filter bands by genre."),
    member_count: int | None = Query(None, description="Filter bands by member count."),
    max_price: float | None = Query(None, description="Show only bands with price less than or equal to this value."),
    sort_by: str | None = Query(None, description="Sort by this column name (like price, name, or member_count)."),
    order: SortOrder = Query(SortOrder.asc, description="Sort order — 'asc' or 'desc'."),
    db: Session = Depends(db.get_db)
):
    model_dict = {
        "name": name,
        "genre": genre,
        "member_count": member_count,
        "max_price": max_price,
        "sort_by": sort_by,
        "order": order
    }
    return service.get_bands(db, model_dict)


@router.get("/decorations")
def get_all_decorations(
    name: str | None = Query(None, description="Filter decorations by name."),
    type: str | None = Query(None, description="Filter decorations by type."),
    max_price: float | None = Query(None, description="Show only decorations with price less than or equal to this value."),
    sort_by: str | None = Query(None, description="Sort by this column name (like price or name)."),
    order: SortOrder = Query(SortOrder.asc, description="Sort order — 'asc' or 'desc'."),
    db: Session = Depends(db.get_db)
):
    model_dict = {
        "name": name,
        "type": type,
        "max_price": max_price,
        "sort_by": sort_by,
        "order": order
    }
    return service.get_decorations(db, model_dict)


@router.get("/snacks")
def get_all_snacks(
    price: float | None = Query(None, description="Filter snacks by price."),
    sort_by: str | None = Query(None, description="Sort by this column name (like price or id)."),
    order: SortOrder = Query(SortOrder.asc, description="Sort order — 'asc' or 'desc'."),
    db: Session = Depends(db.get_db)
):
    model_dict = {
        "price": price,
        "sort_by": sort_by,
        "order": order
    }
    return service.get_snacks(db, model_dict)
