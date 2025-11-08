from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.dependencies import db
from app.services.payment import payment_service
from app.models.enum import PaymentStatus, RoleType

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/all")
def get_all_payments(
    start_date: Optional[date] = Query(None, description="Filter from this payment date"),
    end_date: Optional[date] = Query(None, description="Filter until this payment date"),
    search: Optional[str] = Query(None, description="Search by event or user name"),
    status: Optional[PaymentStatus] = Query(None, description="Payment status filter"),
    role: Optional[RoleType] = Query(None, description="User role filter"), 
    db: Session = Depends(db.get_db)
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")

    if role and role.lower() not in ["audience", "organizer"]:
        raise HTTPException(status_code=400, detail="Role must be either 'audience' or 'organizer'")

    result = payment_service.get_all_payments(
        db=db,
        start_date=start_date,
        end_date=end_date,
        search=search,
        status=status,
        role=role,
    )

    if not result["payments"]:
        raise HTTPException(status_code=404, detail="No payments found")

    return result


