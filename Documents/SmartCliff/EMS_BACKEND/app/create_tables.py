from app.database.connection import Base, engine, SessionLocal
from app.models.user import  UserDetails
from app.models.role import Role
from app.models.events import Event, EventStatusHistory
from app.models.facilities import Venues, Bands, Decorations, Snacks
from app.models.facilities_selected import FacilitiesSelected, Facility_type, FacilityUpdate
from app.models.payment import PaymentAudience, PaymentDetails, PaymentOrganizer, RefundAudience, RefundOrganizer
from app.models.tickets import Tickets



# # Drop all tables (optional reset)
# Base.metadata.drop_all(bind=engine)
# print("✅All tables dropped successfully!")

Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!") 

