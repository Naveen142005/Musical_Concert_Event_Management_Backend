from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.bookings import Bookings, BookingDetails
from app.models.events import Event
from datetime import date, datetime
from typing import Optional


class ReportService:
    
    def get_event_report(self, event_id: int, start_date: Optional[date], end_date: Optional[date], db: Session):
        """Event booking report"""
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            return {"error": "Event not found"}
        
        query = db.query(Bookings).filter(Bookings.event_id == event_id)
        
        if start_date:
            query = query.filter(Bookings.created_at >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            query = query.filter(Bookings.created_at <= datetime.combine(end_date, datetime.max.time()))
        
        bookings = query.all()
        
        return {
            "event_name": event.name,
            "event_date": str(event.event_date),
            "total_bookings": len(bookings),
            "total_tickets": sum(b.total_tickets for b in bookings),
            "total_revenue": sum(b.total_amount for b in bookings)
        }


    def get_all_events_report(self, start_date: Optional[date], end_date: Optional[date], db: Session):
        """All events report"""
        query = db.query(Event)
        
        if start_date:
            query = query.filter(Event.event_date >= start_date)
        if end_date:
            query = query.filter(Event.event_date <= end_date)
        
        events = query.all()
        reports = []
        
        for event in events:
            bookings = db.query(Bookings).filter(Bookings.event_id == event.id).all()
            
            reports.append({
                "event_name": event.name,
                "event_date": str(event.event_date),
                "total_bookings": len(bookings),
                "total_tickets": sum(b.total_tickets for b in bookings),
                "total_revenue": sum(b.total_amount for b in bookings)
            })
        
        return {"events": reports}


    def get_ticket_report(self, start_date: Optional[date], end_date: Optional[date], db: Session):
        """Ticket sales report - Case insensitive grouping"""
        query = db.query(
            func.lower(BookingDetails.ticket_type).label("ticket_type"),
            func.sum(BookingDetails.quantity).label("quantity"),
            func.sum(BookingDetails.sub_total).label("revenue")
        ).join(Bookings)
        
        if start_date:
            query = query.filter(Bookings.created_at >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            query = query.filter(Bookings.created_at <= datetime.combine(end_date, datetime.max.time()))
        
        results = query.group_by(func.lower(BookingDetails.ticket_type)).all()
        
        total_revenue = sum(r.revenue for r in results)
        
        tickets = [
            {
                "ticket_type": r.ticket_type.capitalize(),
                "quantity_sold": r.quantity,
                "revenue": r.revenue,
                "percentage": round((r.revenue / total_revenue * 100) if total_revenue > 0 else 0, 2)
            } for r in results
        ]
        
        return {"tickets": tickets}


report_service = ReportService()
