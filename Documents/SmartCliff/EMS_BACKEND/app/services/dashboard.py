from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, desc
from datetime import datetime, timedelta
from app.models.activity_log import ActivityLog
from app.models.escrow import Escrow
from app.models.user import User
from app.models.events import Event
from app.models.bookings import Bookings
from app.models.tickets import Tickets
from app.models.payment import Payment
from app.models.facilities import *
from app.models.facilities_selected import *
from app.models.enum import BookingStatus, EventStatus, PaymentStatus


class DashboardService:
    
    def get_overview_stats(self, db: Session):
        """Get dashboard overview statistics"""
        
        # Event Statistics
        total_events = db.query(Event).count()
        active_events = db.query(Event).filter(Event.status == EventStatus.BOOKED).count()
        
        today = datetime.now().date()
        upcoming_events = db.query(Event).filter(Event.event_date > today).count()
        past_events = db.query(Event).filter(Event.event_date < today).count()
        
        # Venue and Band counts
        total_venues = db.query(Venues).count()
        total_bands = db.query(Bands).count()
        
        # Booking Statistics
        total_bookings = db.query(Bookings).count()
        
        # Revenue Statistics
        total_revenue_result = db.query(func.sum(Payment.payment_amount)).filter(
            Payment.status == PaymentStatus.COMPLETED
        ).first()
        total_revenue = float(total_revenue_result[0]) if total_revenue_result[0] else 0.0
        
        escrow = db.query(Escrow.released_amount).all()
        escrow_amount = sum(escrow)
        
        total_revenue -= escrow_amount
        # Monthly revenue
        current_month = datetime.now().month
        current_year = datetime.now().year
        monthly_revenue_result = db.query(func.sum(Payment.payment_amount)).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                extract('month', Payment.created_at) == current_month,
                extract('year', Payment.created_at) == current_year
            )
        ).first()
        monthly_revenue = float(monthly_revenue_result[0]) if monthly_revenue_result[0] else 0.0
        
        # Previous month revenue
        last_month = current_month - 1 if current_month > 1 else 12
        last_month_year = current_year if current_month > 1 else current_year - 1
        last_monthly_revenue_result = db.query(func.sum(Payment.payment_amount)).filter(
            and_(
                Payment.status == PaymentStatus.COMPLETED,
                extract('month', Payment.created_at) == last_month,
                extract('year', Payment.created_at) == last_month_year
            )
        ).first()
        last_monthly_revenue = float(last_monthly_revenue_result[0]) if last_monthly_revenue_result[0] else 0.0
        
        # User Statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.status == True).count()
        
        last_month_users = db.query(User).filter(
            and_(
                extract('month', User.created_at) < current_month,
                extract('year', User.created_at) <= current_year
            )
        ).count()
        
        # Ticket Statistics
        total_tickets_result = db.query(func.sum(Tickets.booked_ticket)).first()
        total_tickets_sold = int(total_tickets_result[0]) if total_tickets_result[0] else 0
        
        avg_ticket_result = db.query(func.avg(Tickets.price)).first()
        avg_ticket_price = float(avg_ticket_result[0]) if avg_ticket_result[0] else 0.0
        
        # Top Venues
        venue_type = db.query(Facility_type).filter(Facility_type.facility_type == 'venue').first()
        top_venues = []
        
        if venue_type:
            venue_stats = db.query(
                Venues.id,
                Venues.name,
                func.count(FacilitiesSelected.id).label('usage_count'),
                func.sum(Event.total_amount).label('revenue')
            ).select_from(Venues)\
             .outerjoin(FacilitiesSelected, and_(
                 FacilitiesSelected.facility_id == Venues.id,
                 FacilitiesSelected.facility_type_id == venue_type.id
             ))\
             .outerjoin(Event, Event.id == FacilitiesSelected.event_id)\
             .group_by(Venues.id, Venues.name)\
             .order_by(desc('usage_count'))\
             .limit(5).all()
            
            for v in venue_stats:
                top_venues.append({
                    "venue_id": v.id,
                    "venue_name": v.name,
                    "booking_count": v.usage_count,
                    "revenue": float(v.revenue) if v.revenue else 0.0
                })
        
        # Top Bands
        band_type = db.query(Facility_type).filter(Facility_type.facility_type == 'band').first()
        top_bands = []
        
        if band_type:
            band_stats = db.query(
                Bands.id,
                Bands.name,
                func.count(FacilitiesSelected.id).label('event_count'),
                func.sum(Tickets.booked_ticket).label('total_tickets')
            ).select_from(Bands)\
             .outerjoin(FacilitiesSelected, and_(
                 FacilitiesSelected.facility_id == Bands.id,
                 FacilitiesSelected.facility_type_id == band_type.id
             ))\
             .outerjoin(Event, Event.id == FacilitiesSelected.event_id)\
             .outerjoin(Tickets, Tickets.event_id == Event.id)\
             .group_by(Bands.id, Bands.name)\
             .order_by(desc('event_count'))\
             .limit(5).all()
            
            for b in band_stats:
                top_bands.append({
                    "band_id": b.id,
                    "band_name": b.name,
                    "event_count": b.event_count,
                    "total_tickets": int(b.total_tickets) if b.total_tickets else 0
                })
        
        # Revenue Growth
        revenue_growth_percentage = 0.0
        revenue_trend = "neutral"
        if last_monthly_revenue > 0:
            revenue_growth_percentage = ((monthly_revenue - last_monthly_revenue) / last_monthly_revenue) * 100
            revenue_trend = "up" if revenue_growth_percentage > 0 else "down"
        
        # User Growth
        user_growth_percentage = 0.0
        user_trend = "neutral"
        if last_month_users > 0:
            user_growth_percentage = ((total_users - last_month_users) / last_month_users) * 100
            user_trend = "up" if user_growth_percentage > 0 else "down"
        
        return {
            "total_events": total_events,
            "active_events": active_events,
            "upcoming_events": upcoming_events,
            "past_events": past_events,
            "total_venues": total_venues,
            "total_bands": total_bands,
            "total_bookings": total_bookings,
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
            "total_users": total_users,
            "active_users": active_users,
            "total_tickets_sold": total_tickets_sold,
            "average_ticket_price": avg_ticket_price,
            "top_venues": top_venues,
            "top_bands": top_bands,
            "revenue_growth": {
                "percentage": round(revenue_growth_percentage, 2),
                "trend": revenue_trend,
                "compared_to": "last_month"
            },
            "user_growth": {
                "percentage": round(user_growth_percentage, 2),
                "trend": user_trend,
                "compared_to": "last_month"
            }
        }
    
    def get_recent_activities(self, db: Session, limit: int):
        """Get recent activities from activity log"""
        
        activities = db.query(
            ActivityLog.id,
            ActivityLog.activity_type,
            ActivityLog.title,
            ActivityLog.description,
            ActivityLog.created_at,
            ActivityLog.status,
            ActivityLog.amount,
            ActivityLog.event_id,
            User.id.label('user_id'),
            User.name.label('username'),
            Event.name.label('event_name')
        ).join(User, User.id == ActivityLog.user_id)\
        .outerjoin(Event, Event.id == ActivityLog.event_id)\
        .order_by(desc(ActivityLog.created_at))\
        .limit(limit).all()
        
        result = []
        for a in activities:
            result.append({
                "id": a.id,
                "type": a.activity_type,
                "title": a.title,
                "description": a.description,
                "timestamp": a.created_at.isoformat() if a.created_at else None,
                "status": a.status if a.status else "completed",
                "user_id": a.user_id,
                "username": a.username,
                "event_id": a.event_id,
                "event_name": a.event_name,
                "amount": float(a.amount) if a.amount else None
            })
        
        return result

    # def get_analytics(self, db: Session, period: str):
    #     """Get analytics data"""
        
    #     # Calculate date range
    #     today = datetime.now().date()
    #     if period == "day":
    #         start_date = today - timedelta(days=1)
    #     elif period == "week":
    #         start_date = today - timedelta(days=7)
    #     elif period == "month":
    #         start_date = today - timedelta(days=30)
    #     elif period == "year":
    #         start_date = today - timedelta(days=365)
    #     else:
    #         start_date = today - timedelta(days=7)
        
    #     # Revenue Chart
    #     revenue_data = db.query(
    #         func.date(Payment.created_at).label('date'),
    #         func.sum(Payment.payment_amount).label('revenue')
    #     ).filter(
    #         and_(
    #             Payment.status == PaymentStatus.COMPLETED,
    #             Payment.created_at >= start_date
    #         )
    #     ).group_by(func.date(Payment.created_at)).all()
        
    #     revenue_chart = []
    #     for r in revenue_data:
    #         revenue_chart.append({
    #             "date": str(r.date),
    #             "value": float(r.revenue) if r.revenue else 0.0
    #         })
        
    #     # Bookings Chart
    #     bookings_data = db.query(
    #         func.date(Bookings.created_at).label('date'),
    #         func.count(Bookings.id).label('bookings')
    #     ).filter(Bookings.created_at >= start_date)\
    #      .group_by(func.date(Bookings.created_at)).all()
        
    #     bookings_chart = []
    #     for b in bookings_data:
    #         bookings_chart.append({
    #             "date": str(b.date),
    #             "value": float(b.bookings)
    #         })
        
    #     # Ticket Sales Chart
    #     ticket_sales_data = db.query(
    #         func.date(Bookings.created_at).label('date'),
    #         func.sum(Bookings.total_tickets).label('tickets')
    #     ).filter(Bookings.created_at >= start_date)\
    #      .group_by(func.date(Bookings.created_at)).all()
        
    #     ticket_sales_chart = []
    #     for t in ticket_sales_data:
    #         ticket_sales_chart.append({
    #             "date": str(t.date),
    #             "value": float(t.tickets) if t.tickets else 0.0
    #         })
        
    #     # User Registrations
    #     user_reg_data = db.query(
    #         func.date(User.created_at).label('date'),
    #         func.count(User.id).label('new_users')
    #     ).filter(User.created_at >= start_date)\
    #      .group_by(func.date(User.created_at)).all()
        
    #     user_registrations = []
    #     for u in user_reg_data:
    #         user_registrations.append({
    #             "date": str(u.date),
    #             "value": float(u.new_users)
    #         })
        
    #     # Event Distribution
    #     event_distribution = []
        
    #     # Payment Methods
    #     payment_method_data = db.query(
    #         Payment.payment_mode,
    #         func.count(Payment.id).label('count')
    #     ).filter(Payment.status == PaymentStatus.COMPLETED)\
    #      .group_by(Payment.payment_mode).all()
        
    #     total_payments = sum([p.count for p in payment_method_data])
    #     payment_methods = []
    #     for p in payment_method_data:
    #         payment_methods.append({
    #             "method": p.payment_mode if p.payment_mode else "unknown",
    #             "percentage": float((p.count / total_payments * 100) if total_payments > 0 else 0)
    #         })
        
    #     # Top Selling Events
    #     top_events = db.query(
    #         Event.id,
    #         Event.name,
    #         func.sum(Tickets.booked_ticket).label('tickets_sold'),
    #         func.sum(Bookings.total_amount).label('revenue')
    #     ).join(Tickets, Tickets.event_id == Event.id)\
    #      .join(Bookings, Bookings.event_id == Event.id)\
    #      .group_by(Event.id, Event.name)\
    #      .order_by(desc('tickets_sold'))\
    #      .limit(10).all()
        
    #     top_selling_events = []
    #     for e in top_events:
    #         top_selling_events.append({
    #             "event_id": e.id,
    #             "event_name": e.name,
    #             "tickets_sold": int(e.tickets_sold) if e.tickets_sold else 0,
    #             "revenue": float(e.revenue) if e.revenue else 0.0
    #         })
        
    #     return {
    #         "period": period,
    #         "start_date": str(start_date),
    #         "end_date": str(today),
    #         "revenue_chart": revenue_chart,
    #         "bookings_chart": bookings_chart,
    #         "ticket_sales_chart": ticket_sales_chart,
    #         "user_registrations": user_registrations,
    #         "event_distribution": event_distribution,
    #         "payment_methods": payment_methods,
    #         "top_selling_events": top_selling_events
    #     }


dashboard_service = DashboardService()
