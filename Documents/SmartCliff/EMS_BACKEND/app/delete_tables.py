from app.database.connection import Base, engine
from app.models.user import User
from app.models.role import Role
from app.models.events import Event
from app.models.facilities import Venues, Bands, Decorations, Snacks
from app.models.facilities_selected import EventFacilities, FacilityUpdate


Base.metadata.drop_all(bind=engine)
print("✅ All tables dropped successfully!")
