from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Literal, Optional, List
from app.models.enum import EventStatus

class EventBase(BaseModel):
    
    event_name: str = Field(..., title="Event Name")
    description: str = Field(..., title="Description")
    slot: Literal["Morning", "Afternoon", "Night"] = Field(..., title="Slot")
    event_date: date = Field(..., title="Event Date")
    venue_id: Optional[int] = Field(None, title="Venue ID")
    band_id: Optional[int] = Field(None, title="Band ID")
    decoration_id: Optional[int] = Field(None, title="Decoration ID")
    snacks_id: Optional[int] = Field(None, title="Snacks ID")
    snacks_count: Optional[int] = Field(None, title="Snacks Count")
    ticket_enabled: Optional[bool] = Field(False, title="Ticket Enabled")
    platinum_ticket_price: Optional[int] = Field(None, title="Platinum Ticket Price")
    platinum_ticket_count: Optional[int] = Field(None, title="Count of the platinum ticket")
    gold_ticket_price: Optional[int] = Field(None, title="Gold Ticket Price")
    gold_ticket_count: Optional[int] = Field(None, title="Count of the gold ticket")
    silver_ticket_price: Optional[int] = Field(None, title="Silver Ticket Price")
    silver_ticket_count: Optional[int] = Field(None, title="Count of the Silver ticket")    
    payment_type: Literal["Full payment", "Half payment"] = Field(..., title= "Payment Type")
    payment_mode: Literal["UPI", "Credit Card", "Debit Card"] = Field(..., title="Payment Mode")
    payment_amount:int = Field(..., title="total amount")
    


class EventResponse(EventBase):
    id: int
    user_id: int
    created_at: date
    status: EventStatus
    user_id: int
    payment_id: int

    class Config:
        orm_mode = True
