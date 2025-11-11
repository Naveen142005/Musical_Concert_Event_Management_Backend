from fastapi import APIRouter
from datetime import datetime
from app.routers.websocket import notify_admins

router = APIRouter()

@router.get("/create_event")
async def test_create_event():
    await notify_admins({
        "event_id": 101,
        "action": "created",
        "user_id": 7,
        "event_name": "Birthday Party",
        "timestamp": datetime.now().isoformat()
    })
    return {"message": "Create event notification sent!"}

@router.get("/cancel_event")
async def test_cancel_event():
    await notify_admins({
        "event_id": 105,
        "action": "cancelled",
        "reason": "Organizer cancelled",
        "timestamp": datetime.now().isoformat()
    })
    return {"message": "Cancel event notification sent!"}

@router.get("/reschedule_event")
async def test_reschedule_event():
    await notify_admins({
        "event_id": 103,
        "action": "rescheduled",
        "old_date": "2025-11-10",
        "new_date": "2025-11-15",
        "timestamp": datetime.now().isoformat()
    })
    return {"message": "Reschedule event notification sent!"}

@router.get("/pending_payment")
async def test_pending_payment():
    await notify_admins({
        "event_id": 107,
        "action": "pending_payment",
        "user_id": 12,
        "amount": 5000,
        "timestamp": datetime.now().isoformat()
    })
    return {"message": "Pending payment notification sent!"}
