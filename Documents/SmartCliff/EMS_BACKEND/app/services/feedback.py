from typing import Optional
from fastapi import HTTPException
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session
import resend
from app.models.bookings import Bookings
from app.models.events import Event

from app.models.feedback import Feedback
from app.models.role import Role
from app.models.user import User
from app.utils.common import encode_ids, get_row, raise_exception, send_email
import base64


class FeedBack:
    async def send_feedback(self, id: int, user_id: int, db:Session):
        
        role, event_name, event_date, feedback_link, receiver_email = feedback_service.get_info_for_feedback(id, db, user_id)
        
        # Customize message based on user type
        if role == "organizer":
            greeting = "Hi Organizer!"
            message = f"Your event <strong>{event_name}</strong> on {event_date} was successfully Completed."
        else:  # audience
            greeting = "Hi there!"
            message = f"Thank you for attending <strong>{event_name}</strong> on {event_date}."

        html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.5;">
                <h3>{greeting}</h3>
                <p>{message}</p>
                <p>Please click the button below to submit your feedback:</p>
                <p style="text-align: center;">
                    <a href="{feedback_link}" style="
                        display: inline-block;
                        background-color: #4CAF50;
                        color: white;
                        padding: 12px 20px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;">
                        Submit Feedback
                    </a>
                </p>
                <p>If the button does not work, copy this link in your browser:</p>
                <p><a href="{feedback_link}">{feedback_link}</a></p>
            </body>
        </html>
        """
        
        try:
            send_email(receiver_email, "Event Feedback Request", html)
            return {"status": "Email sent successfully", "to": receiver_email}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

 
    def get_info_for_feedback(self, id: int, db: Session, user_id):
        # Get event and user
        user_data: User = get_row(db, User, id=user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        role = "audience"
        print ((user_data.role.name).lower())
        if (user_data.role.name).lower() == "organizer":
            
            event_data: Event = get_row(db, Event, id=id, user_id = user_id)
            if not event_data:
                raise HTTPException(status_code=404, detail="Event not found")
        
            token = encode_ids(event_data.id, user_data.id)
            created_date = event_data.created_at.strftime("%Y-%m-%d")
            role = "organizer"
            
        else:
            booking_data: Bookings = get_row(db, Bookings, id=id, user_id = user_id)
            event_data = get_row(db, Event, id=booking_data.event_id)
            
            if not booking_data:
                raise HTTPException(status_code=404, detail="Event not found")
            
            token = encode_ids(booking_data.id, user_data.id)
            created_date= booking_data.created_at.strftime("%Y-%m-%d")

        
        
        feedback_link = f"http://localhost:8000/feedback/form?token={token}"
        
        return [
            role,
            event_data.name,
            created_date,
            feedback_link,
            user_data.email
        ]
        

    
    def get_all_feedback(
        self,
        db: Session,
        rating: Optional[int] = None,
        status: Optional[str] = None
    ):
        query = (db.query(
            Feedback,
            Event.name.label("event_name"),
            User.name.label("user_name")
        ).join(Event, Feedback.event_id == Event.id)
         .join(User, Feedback.user_id == User.id))

        if rating is not None:
            query = query.filter(Feedback.feedback_rating == rating)
        if status is not None:
            query = query.filter(Feedback.status == status)

        feedbacks = query.order_by(desc(Feedback.feedback_date)).all()

        result = []
        for fb, event_name, user_name in feedbacks:
            result.append({
                "id": fb.id,
                "user_name": user_name,
                "event_name": event_name,
                "feedback_rating": fb.feedback_rating,
                "feedback_summary": fb.feedback_summary,
                "feedback_date": fb.feedback_date,
                "status": fb.status
            })
        return result

    def mark_feedback_read(self, db: Session, feedback_id: int):
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        feedback.status = "read"
        db.commit()
        db.refresh(feedback)
        return {"status": "Feedback marked as read", "feedback_id": feedback.id, "new_status": feedback.status}

    def delete_feedback(self, db: Session, feedback_id: int):
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        db.delete(feedback)
        db.commit()
        return {"status": "Feedback deleted successfully", "feedback_id": feedback_id}


    def get_my_event_feedback(self ,event_id: int, user_id: int, db: Session):
        # Step 1: Check event existence
        event_data = get_row(db, Event, id=event_id)
        if not event_data:
            raise_exception(404, "Event not found")

        # Step 2: Check if feedback is enabled
        if not event_data.ticket_enabled:
            raise_exception(403, "This event doesn't have feedback option")

        # Step 3: Verify event ownership
        if event_data.user_id != user_id:
            raise_exception(404, "Event not found. (This event not belongs to this user_id)")

        # Step 4: Fetch feedback only from audience
        feedback_data = (
            db.query(Feedback, User, Role)
            .join(User, Feedback.user_id == User.id)
            .join(Role, User.role_id == Role.id)
            .filter(
                and_(
                    Feedback.event_id == event_id,
                    func.lower(Role.name) == "audience"
                )
            )
            .all()
        )

        # Step 5: Handle no feedback case
        if not feedback_data:
            return {"message": "No feedback submitted for this event yet"}

        # Step 6: Structure the JSON response
        response = {
            "event_id": event_id,
            "event_name": event_data.name,
            "total_feedbacks": len(feedback_data),
            "feedbacks": []
        }

        for feedback, user, role in feedback_data:
            response["feedbacks"].append({
                "feedback_id": feedback.id,
                "audience_name": user.name,
                "email": user.email,
                "rating": feedback.feedback_rating,
                "summary": feedback.feedback_summary,
                "feedback_date": feedback.feedback_date.strftime("%Y-%m-%d %H:%M:%S"),
                "status": feedback.status,
                "role": role.name
            })

        return response


feedback_service = FeedBack()
