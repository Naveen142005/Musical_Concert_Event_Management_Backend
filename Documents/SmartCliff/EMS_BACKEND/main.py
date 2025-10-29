from fastapi import FastAPI

from app.routers import user
from app.routers import facility
from app.routers import events

application = FastAPI()
application.include_router(user.router, tags=["Users"])
application.include_router(facility.router, tags=["Facilities"])
application.include_router(events.router, tags=['Events'], prefix='/events')