import os
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.auth.auth_utils import role_requires
from app.dependencies import db
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    RecentActivitiesResponse,
    AnalyticsResponse
)
from app.services.dashboard import dashboard_service


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(db_session: Session = Depends(db.get_db),current_user: dict = Depends(role_requires("Admin"))):
    """Get dashboard overview statistics"""
    overview = dashboard_service.get_overview_stats(db=db_session)
    return overview


@router.get("/recent-activities", response_model=RecentActivitiesResponse)
def get_recent_activities(limit: int = 10, db_session: Session = Depends(db.get_db),current_user: dict = Depends(role_requires("Admin"))):
    """Get recent activities"""
    activities = dashboard_service.get_recent_activities(db=db_session, limit=limit)
    return {"activities": activities}


# @router.get("/analytics", response_model=AnalyticsResponse)
# def get_analytics(period: str = "week", db_session: Session = Depends(db.get_db),current_user: dict = Depends(role_requires("Admin"))):
#     """Get analytics data for specified period (day, week, month, year)"""
#     analytics = dashboard_service.get_analytics(db=db_session, period=period)
#     return analytics


@router.get("/dashboard")
async def dashboard():
    file_path = os.path.join(os.getcwd(), "templates", "dashboard.html")
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content= html_content)