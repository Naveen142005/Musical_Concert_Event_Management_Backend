import os
from dark_swag import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.routers import test, user,websocket
from app.routers import facility
from app.routers import events
from app.routers import booking,payments
from app.routers import feedback
from app.routers import query
application = FastAPI() 
templates = Jinja2Templates(directory="templates") 

application.include_router(user.router, tags=["Users"], prefix="/users")
application.include_router(facility.router, tags=["Facilities"])
application.include_router(events.router, tags=['Events'], prefix='/events')
application.include_router(booking.router, tags=["Bookings"])
application.include_router(payments.router)
application.include_router(feedback.router, tags=["feedback "], prefix="/feedback")
application.include_router(query.router)
application.include_router(query.router_)
application.include_router(test.router)
application.include_router(websocket.router)

@application.get("/dashboard")
async def dashboard():
    file_path = os.path.join(os.getcwd(), "templates", "dashboard.html")
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content= html_content)