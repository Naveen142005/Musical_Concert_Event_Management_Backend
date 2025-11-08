from typing import Optional
from fastapi import APIRouter, Form, HTTPException, Depends, Query, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.dependencies import db

from app.models.feedback import Feedback
from app.utils.common import decode_ids  # make a decode_ids function
from app.services.feedback import feedback_service


router = APIRouter()
templates = Jinja2Templates(directory="templates") 

@router.post("/send-feedback")
async def send_feedback_test(event_id: int, user_type:str, user_id: int, db: Session = Depends(db.get_db)):

    try:
        result = await feedback_service.send_feedback(event_id, user_type, user_id, db)
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
    status: Optional[str] = Query(None, description="Filter by feedback status ('submitted', 'read')")
):
    return feedback_service.get_all_feedback(db=db, rating=rating, status=status)

# ---------------------------
# UPDATE feedback status to read
# ---------------------------
@router.put("/{feedback_id}/read")
async def mark_feedback_read(feedback_id: int, db: Session = Depends(db.get_db)):
    return feedback_service.mark_feedback_read(db=db, feedback_id=feedback_id)

# ---------------------------
# DELETE feedback
# ---------------------------
@router.delete("/{feedback_id}")
async def delete_feedback(feedback_id: int, db: Session = Depends(db.get_db)):
    return feedback_service.delete_feedback(db=db, feedback_id=feedback_id)