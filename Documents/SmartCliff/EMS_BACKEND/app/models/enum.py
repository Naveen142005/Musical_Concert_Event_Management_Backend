from enum import Enum


from enum import Enum

class PaymentMode(str, Enum):
    UPI = "upi"
    CREDIT_CARD = "credit_card"
    

class BookingStatus(str, Enum):
    BOOKED = "booked"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
# ==========================
# Event Status Enum
# ==========================
class EventStatus(str, Enum):
    BOOKED = "booked"
    RESCHEDULED = "rescheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ONGOING = "ongoing"

class SlotEnum(str, Enum):
    morning = "Morning"
    afternoon = "Afternoon"
    night = "Night"



class DateType(str, Enum):
    BOOKED_DATE = "booked_date"
    EVENT_DATE = "event_date"


# ==========================
# Payment Status Enum
# ==========================
class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    REFUND_INITIATED = "refund_initiated"

# ==========================
# Refund Status Enum
# ==========================
class RefundStatus(str, Enum):
    INITIATED = "initiated"
    PROCESSED = "processed"
    COMPLETED = "completed"
    REJECTED = "rejected"

class RoleType(str, Enum):
    audience = "audience"
    organizer = "organizer"


# ==========================
# User Role Enum
# ==========================
class UserRole(str, Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    AUDIENCE = "audience"



class FacilityStatus(str, Enum):
    AVAILABLE = "available"
    Deactivated = "deactivated"
    UNDER_MAINTENANCE = "under_maintenance"
    
class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"