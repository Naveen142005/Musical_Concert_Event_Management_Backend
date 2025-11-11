from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.auth_utils import role_requires
from app.dependencies import db
from datetime import date
from typing import Optional
from app.schemas.report import EventReport, TicketReport
from typing import List
from app.services.report import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/event/{event_id}", response_model=EventReport)
def event_report(
    event_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(db.get_db),
        current_user: dict = Depends(role_requires("Admin"))
):
    return report_service.get_event_report(event_id, start_date, end_date, db)


@router.get("/events")
def all_events_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(db.get_db),
        current_user: dict = Depends(role_requires("Admin"))
):
    return report_service.get_all_events_report(start_date, end_date, db)


@router.get("/tickets")
def ticket_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(db.get_db),
    current_user: dict = Depends(role_requires("Admin"))
):
    return report_service.get_ticket_report(start_date, end_date, db)
