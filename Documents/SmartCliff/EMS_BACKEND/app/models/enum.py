from enum import Enum


from enum import Enum

class BookingStatus(str, Enum):
    BOOKED = "booked"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    REFUNDED = "refunded"
    PENDING = "pending"
    FAILED = "failed"
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



# ==========================
# User Role Enum
# ==========================
class UserRole(str, Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    AUDIENCE = "audience"

class FacilityStatus(str, Enum):
    AVAILABLE = "available"
    BOOKED = "booked"
    Deactivated = "deactivated"
    UNDER_MAINTENANCE = "under_maintenance"
    
class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"