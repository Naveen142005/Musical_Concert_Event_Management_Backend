from pydantic import BaseModel, Field, conint, constr, field_validator, validator
from typing import List, Literal

# --- Request models ---

class TicketRequest(BaseModel):
    ticket_type: str = Field(..., description="Ticket type name (Platinum, Gold, Silver)")
    quantity: int = Field(..., gt=0, description="Number of tickets to book")

    @field_validator("ticket_type")
    def normalize_ticket_type(cls, v):
        valid_types = {"Platinum", "Gold", "Silver"}
        if v not in valid_types:
            raise ValueError(f"Invalid ticket type. Choose from: {valid_types}")
        return v


class BookingCreate(BaseModel):
    event_id: int = Field(..., gt=0)
    tickets: List[TicketRequest]
    payment_mode: Literal["UPI", "Credit Card", "Debit Card"] = Field(..., title="Payment Mode")

# --- Response models ---

class TicketSummary(BaseModel):
    ticket_type: Literal["Platinum", "Gold", "Silver"]
    quantity: int
    subtotal: float


class BookingResponse(BaseModel):
    booking_id: int
    user_id: int
    event_id: int
    tickets: List[TicketSummary]
    total_tickets: int
    total_price: float
    status: Literal["booked", "cancelled"]
