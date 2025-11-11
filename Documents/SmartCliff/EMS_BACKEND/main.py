import time
import os
import logging
from dark_swag import FastAPI
from fastapi import BackgroundTasks, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager


from app.routers import test, user, websocket
from app.routers import facility
from app.routers import events
from app.routers import booking, payments
from app.routers import feedback
from app.routers import query
from app.routers import content_management
from app.routers import dashboard, backup
from app.routers import report, terms
from app.services.backup_service import is_maintenance_mode
from app.utils.scheduler import start_scheduler


from pathlib import Path
Path("logs").mkdir(exist_ok=True)


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/activity.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Lifespan for scheduler
@asynccontextmanager
async def lifespan(application: FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()


# Initialize FastAPI with lifespan
application = FastAPI(lifespan=lifespan) 
templates = Jinja2Templates(directory="templates") 


# Include routers
# Include routers
application.include_router(user.router, tags=["Users"], prefix="/users")
application.include_router(user.router_admin)
application.include_router(facility.router)
application.include_router(events.router, tags=['Events'], prefix='/events')
application.include_router(booking.router, tags=["Bookings"])
application.include_router(payments.router, tags=["Payments"])
application.include_router(feedback.router, tags=["Feedback"], prefix="/feedback")
application.include_router(query.router)
application.include_router(query.router_, tags=["Admin Queries"])
application.include_router(test.router, tags=["Testing"])
application.include_router(websocket.router, tags=["WebSocket"])
application.include_router(content_management.router, prefix="/contents", tags=["Content Management"])
application.include_router(terms.router)
application.include_router(dashboard.router, tags=["Dashboard"])
application.include_router(report.router)
application.include_router(backup.router)
 
@application.middleware("http")
async def maintenance_mode_middleware(request: Request, call_next):

    
    start_time = time.time()
    
    client_ip = request.client.host
    method = request.method
    path = request.url.path
    
    if is_maintenance_mode():
        if request.url.path.startswith("/backup"):
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(f"[MAINTENANCE] {method} {path} | IP: {client_ip} | Status: {response.status_code} | Time: {process_time:.2f}s")
            return response
        
        logger.warning(f"[BLOCKED] {method} {path} | IP: {client_ip} | Reason: System under maintenance")
        
        return JSONResponse(
            status_code=503,
            content={
                "message": "⚠️ System under maintenance. Database restore in progress. Please try again in a few minutes."
            }
        )
    
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{method} {path} | IP: {client_ip} | Status: {response.status_code} | Time: {process_time:.2f}s")
    
    return response
