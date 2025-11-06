from dark_swag import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

from app.routers import user
from app.routers import facility
from app.routers import events
from app.routers import booking


application = FastAPI()  # Disable default docs

application.include_router(user.router, tags=["Users"])
application.include_router(facility.router, tags=["Facilities"])
application.include_router(events.router, tags=['Events'], prefix='/events')
application.include_router(booking.router, tags=["Bookings"])


