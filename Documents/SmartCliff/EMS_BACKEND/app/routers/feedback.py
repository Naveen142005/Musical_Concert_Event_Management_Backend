from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Form, HTTPException, Depends, Query, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth.auth_utils import role_requires
from app.dependencies import db

from app.models.feedback import Feedback
from app.utils.common import decode_ids  # make a decode_ids function
from app.services.feedback import feedback_service


router = APIRouter()
templates = Jinja2Templates(directory="templates") 

@router.post("/send-feedback")
async def send_feedback_test(id: int,  user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(db.get_db)):
    """
                Id can be either Event id or Booking Id\n
                Event id -> To send feedback link to organizer\n
                Booking id -> To send feedback link to audience
    """
    try:
        result = await feedback_service.send_feedback(id, user_id, db, background_tasks)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/form")
async def feedback_form(request: Request, token: str):
    event_id, user_id = decode_ids(token)
    return templates.TemplateResponse("feedback_form.html", {
        "request": request,
        "token": token,
        "event_id": event_id,
        "user_id": user_id
    })

@router.post("/submit")
async def submit_feedback(token: str = Form(...), feedback_rating: int = Form(...), feedback_summary: str = Form(None), db: Session = Depends(db.get_db)):

    event_id, user_id = decode_ids(token)

    new_feedback = Feedback(
        user_id=user_id,
        event_id=event_id,
        feedback_rating=feedback_rating,
        feedback_summary=feedback_summary
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)

    return {"status": "Feedback submitted successfully", "feedback_id": new_feedback.id}

@router.get("/")
async def get_all_feedback(
    db: Session = Depends(db.get_db),
    rating: Optional[int] = Query(None, description="Filter by feedback rating"),
    status: Optional[str] = Query(None, description="Filter by feedback status ('submitted', 'read')"),
    current_user: dict = Depends(role_requires("Admin"))
):
    return feedback_service.get_all_feedback(db=db, rating=rating, status=status)

# ---------------------------
# UPDATE feedback status to read
# ---------------------------
@router.put("/{feedback_id}/read")
async def mark_feedback_read(feedback_id: int, db: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    return feedback_service.mark_feedback_read(db=db, feedback_id=feedback_id)

# ---------------------------
# DELETE feedback
# ---------------------------
@router.delete("/{feedback_id}")
async def delete_feedback(feedback_id: int, db: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    return feedback_service.delete_feedback(db=db, feedback_id=feedback_id)

@router.get("/get_feedback/{event_id}")
def get_my_event_feedback (event_id: int, db: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Organizer"))):
    user_id = current_user["id"]
    return feedback_service.get_my_event_feedback(event_id, user_id, db)
    