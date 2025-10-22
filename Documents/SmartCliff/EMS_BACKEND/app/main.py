from fastapi import FastAPI

from app.routers.users.user import router



application = FastAPI()
application.include_router(router, tags=["Users"])