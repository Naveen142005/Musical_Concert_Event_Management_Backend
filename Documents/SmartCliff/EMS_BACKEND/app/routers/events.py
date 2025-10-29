from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException
from typing import Optional, Literal
from datetime import date, datetime
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.models.events import Event
from app.models.facilities import Venues
from app.models.payment import PaymentDetails, PaymentOrganizer
from app.schemas.event import EventBase, EventResponse
from app.models.enum import EventStatus, PaymentStatus
from app.dependencies import db
from app.crud.event import event

router = APIRouter()




@router.post('/create_new_event', response_model=EventResponse)
async def create_new_event(event_data:EventBase,  db:Session = Depends(db.get_db)):
    created_event = await event.create_new_event(event_data, db)
    return created_event