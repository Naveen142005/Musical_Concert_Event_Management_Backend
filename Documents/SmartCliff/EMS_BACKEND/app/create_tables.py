from app.database.connection import Base, engine, SessionLocal
from app.models.user import  UserDetails
from app.models.role import Role
from app.models.events import Event, EventStatusHistory
from app.models.facilities import Venues, Bands, Decorations, Snacks
from app.models.facilities_selected import FacilitiesSelected, Facility_type, FacilityUpdate
from app.models.payment import Payment, PaymentStatusHistory
from app.models.refund import Refund, RefundStatusHistory
from app.models.tickets import Tickets
from app.models.bookings import Bookings, BookingDetails
from app.models.feedback import Feedback
from app.models.query import Query

# # Drop all tables (optional reset)
# Base.metadata.drop_all(bind=engine)
# print("✅All tables dropped successfully!")

Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!") 




