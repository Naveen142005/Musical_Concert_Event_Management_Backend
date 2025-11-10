from pydantic import BaseModel
from typing import List, Optional


class VenueStats(BaseModel):
    venue_id: int
    venue_name: str
    booking_count: int
    revenue: float


class BandStats(BaseModel):
    band_id: int
    band_name: str
    event_count: int
    total_tickets: int


class GrowthStats(BaseModel):
    percentage: float
    trend: str
    compared_to: str


class DashboardOverviewResponse(BaseModel):
    total_events: int
    active_events: int
    upcoming_events: int
    past_events: int
    total_venues: int
    total_bands: int
    total_bookings: int
    total_revenue: float
    monthly_revenue: float
    total_users: int
    active_users: int
    total_tickets_sold: int
    average_ticket_price: float
    top_venues: List[VenueStats]
    top_bands: List[BandStats]
    revenue_growth: GrowthStats
    user_growth: GrowthStats


class ActivityItem(BaseModel):
    id: int
    type: str
    title: str
    description: str
    timestamp: str
    status: str
    user_id: Optional[int] = None
    username: Optional[str] = None
    amount: Optional[float] = None


class RecentActivitiesResponse(BaseModel):
    activities: List[ActivityItem]


class ChartData(BaseModel):
    date: str
    value: float


class EventDistribution(BaseModel):
    category: str
    count: int


class PaymentMethodDistribution(BaseModel):
    method: str
    percentage: float


class TopEvent(BaseModel):
    event_id: int
    event_name: str
    tickets_sold: int
    revenue: float


class AnalyticsResponse(BaseModel):
    period: str
    start_date: str
    end_date: str
    revenue_chart: List[ChartData]
    bookings_chart: List[ChartData]
    ticket_sales_chart: List[ChartData]
    user_registrations: List[ChartData]
    event_distribution: List[EventDistribution]
    payment_methods: List[PaymentMethodDistribution]
    top_selling_events: List[TopEvent]
