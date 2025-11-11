from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationInfo, model_validator
from datetime import date, datetime, timedelta
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
    ticket_open_date: Optional[date] = Field(None, title="Ticket opeing date")
    platinum_ticket_price: Optional[int] = Field(None,  title="Platinum Ticket Price")
    platinum_ticket_count: Optional[int] = Field(None,  title="Count of the platinum ticket")
    gold_ticket_price: Optional[int] = Field(None,  title="Gold Ticket Price")
    gold_ticket_count: Optional[int] = Field(None,  title="Count of the gold ticket")
    silver_ticket_price: Optional[int] = Field(None,  title="Silver Ticket Price")
    silver_ticket_count: Optional[int] = Field(None,  title="Count of the Silver ticket")    
    payment_type: Literal["Full Payment", "Half Payment"] = Field(..., title= "Payment Type")
    payment_mode: Literal["UPI", "Credit Card", "Debit Card"] = Field(..., title="Payment Mode")
    
    @field_validator("event_name")
    @classmethod
    def validate_event_name(cls, v):
        if not v.replace(" ", "").isalnum():
            raise ValueError("Event name must contain only letter or numbers..")
        return v.strip()

    @field_validator("event_date")
    @classmethod
    def validate_event_date(cls, v):
        tomorrow = date.today() + timedelta(days=1)
        if v < tomorrow:
            raise ValueError("Event date must be at least one day after today.")
        return v
  
    @model_validator(mode="after")
    def validate_facilities(self):
        if self.venue_id == 0:
            self.venue_id = None
        if self.band_id == 0:
            self.band_id = None
        if self.decoration_id == 0:
            self.decoration_id = None
        if self.snacks_id == 0:
            self.snacks_id = None

        if not self.venue_id and not self.band_id:
            raise ValueError("Either 'venue_id' or 'band_id' must be provided.")

        if self.venue_id is not None and self.venue_id < 0:
            raise ValueError("'venue_id' cannot be negative.")
        if self.band_id is not None and self.band_id < 0:
            raise ValueError("'band_id' cannot be negative.")
        if self.decoration_id is not None and self.decoration_id < 0:
            raise ValueError("'decoration_id' cannot be negative.")
        if self.snacks_id is not None and self.snacks_id < 0:
            raise ValueError("'snacks_id' cannot be negative.")

        if self.snacks_id:
            if not self.snacks_count or self.snacks_count <= 0:
                raise ValueError("Enter how many snack boxes you want.")
        elif self.snacks_count not in (None, 0):
            raise ValueError("Remove snacks_count when no snacks are selected.")

        return self

    @model_validator(mode="after")
    def validate_ticket_logic(self):
        self.platinum_ticket_price = None if self.platinum_ticket_price == 0 else self.platinum_ticket_price
        self.platinum_ticket_count = None if self.platinum_ticket_count == 0 else self.platinum_ticket_count
        self.gold_ticket_price = None if self.gold_ticket_price == 0 else self.gold_ticket_price
        self.gold_ticket_count = None if self.gold_ticket_count == 0 else self.gold_ticket_count
        self.silver_ticket_price = None if self.silver_ticket_price == 0 else self.silver_ticket_price
        self.silver_ticket_count = None if self.silver_ticket_count == 0 else self.silver_ticket_count

        if self.ticket_enabled:
            required_fields = {
                "platinum_ticket_price": self.platinum_ticket_price,
                "platinum_ticket_count": self.platinum_ticket_count,
                "gold_ticket_price": self.gold_ticket_price,
                "gold_ticket_count": self.gold_ticket_count,
                "silver_ticket_price": self.silver_ticket_price,
                "silver_ticket_count": self.silver_ticket_count,
            }

            missing = [f for f, v in required_fields.items() if v is None]
            if missing:
                raise ValueError(f"Missing required ticket fields: {', '.join(missing)}")

            for f, v in required_fields.items():
                if v <= 0:
                    raise ValueError(f"'{f}' must be greater than 0 when tickets are enabled.")

        else:
            has_tickets = any([
                self.platinum_ticket_price, self.platinum_ticket_count,
                self.gold_ticket_price, self.gold_ticket_count,
                self.silver_ticket_price, self.silver_ticket_count
            ])
            if has_tickets:
                raise ValueError("Remove ticket details or set 'ticket_enabled' to true.")

        return self



    @model_validator(mode="after")
    def validate_ticket_prices(self):
        p = None if self.platinum_ticket_price  == 0 else self.platinum_ticket_price 
        g = None if self.gold_ticket_price  == 0 else self.gold_ticket_price 
        s = None if self.silver_ticket_price  == 0 else self.silver_ticket_price 

      
        if None in (p, g, s):
            return self

        if not (p > g > s):
            raise ValueError(
                f"Invalid price order: Platinum({p}) > Gold({g}) > Silver({s}) required."
            )

        return self
    
    
    

    @model_validator(mode="after")
    def validate_ticket_open_date(self):
        is_ticket_enabled = self.ticket_enabled
        print(is_ticket_enabled)
        if is_ticket_enabled:
            event_date = self.event_date
            today = date.today()
        
            if self.event_date is None:
               raise ValueError("Event date should be provide")
            
            if self.ticket_open_date is None:
                raise ValueError("Ticketing opening date should be provide.")

            if self.ticket_open_date < today:
                raise ValueError("Ticket opening date cannot be before today.")

            if self.ticket_open_date >= event_date:
                raise ValueError("Ticket opening date must be before the event date.")

            return self
        return self



class EventResponse(EventBase):
    id: int
    user_id: int
    created_at: date
    status: EventStatus
    user_id: int
    payment_id: int
    total_amount: int
    paid_amount: int
    class Config:
        from_attributes = True



class RescheduleEventRequest(BaseModel):
    event_id: int
    excepted_date: date
    ticket_opening_date: date | None = None
    slot: Literal["Morning", "Afternoon", "Night"] = Field(..., title="Slot")


class CancelMailSchema(BaseModel):
    name: str
    email: EmailStr
    event_name: str
    event_date: date
    refund_amount: int
    refund_days: int
    refund_status_url: str

class RescheduleMailSchema(BaseModel):
    name: str
    email: EmailStr
    event_name: str
    old_date: date
    new_date: date
    cancel_before: date
    amount : int