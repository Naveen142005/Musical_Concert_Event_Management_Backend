from pydantic import BaseModel
from typing import List
from datetime import date


class EventReport(BaseModel):
    event_name: str
    event_date: str
    total_bookings: int
    total_tickets: int
    total_revenue: int


class TicketReport(BaseModel):
    ticket_type: str
    quantity_sold: int
    revenue: int
    percentage: float
