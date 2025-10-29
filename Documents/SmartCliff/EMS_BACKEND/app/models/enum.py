from enum import Enum


# ==========================
# Event Status Enum
# ==========================
class EventStatus(str, Enum):
    BOOKED = "booked"
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"


# ==========================
# Payment Status Enum
# ==========================
class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


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