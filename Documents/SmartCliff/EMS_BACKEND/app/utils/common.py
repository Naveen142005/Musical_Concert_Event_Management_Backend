
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.activity_log import ActivityLog
from app.models.enum import EventStatus
from app.models.user import User
from app.models.events import Event
import base64
from datetime import datetime, time, timedelta, timezone
import os
from fastapi import HTTPException, UploadFile
from pytest import Session
from sqlalchemy import and_
import yagmail
from apscheduler.schedulers.background import BackgroundScheduler
from app.schemas.event import CancelMailSchema, RescheduleMailSchema
def model_dumb(model):

    if not model:
        return None
    return {
        column.name: getattr(model, column.name) for column in model.__table__.columns
    }

def commit(db: Session):
    db.commit()

def get_row(db: Session, model_class, **kwargs):
    query = db.query(model_class)
    where_list = []
    
    for key, value in kwargs.items():
        attr = getattr(model_class, key)
        where_list.append(attr == value)     
    
    query = query.filter(and_(*where_list)).first()

    return query if query else None

def get_rows(db: Session, model_class, **kwargs):
    query = db.query(model_class)
    where_list = []
    
    for key, value in kwargs.items():
        attr = getattr(model_class, key)
        where_list.append(attr == value)
    
    query = query.filter(and_(*where_list)).all()

    return query if query else None



def insert_data_flush(db:Session, model_class,  **kwargs):
    new_data = model_class(**kwargs)
    db.add(new_data)
    db.flush()
 
    return new_data

def insert_data(db:Session, model_class,  **kwargs):
    new_data = model_class(**kwargs)
    db.add(new_data)
   
   
    return {key: value for key, value in kwargs.items()}

def update_data(db:Session, model_class, *args ,**kwargs):
   
    query = db.query(model_class).filter(*args).first()
    
    conditions = []
    
    print(args  )
    print(kwargs)
    if not query:
        raise HTTPException(status_code=404, detail="data not found")
    for key, value in kwargs.items():
        if hasattr(query, key):
            setattr(query, key, value)

   
    return query


def delete_data(db: Session, model_class, *args):
    records = db.query(model_class).filter(*args).all()
    if not records:
        raise HTTPException(status_code=404, detail="Data not found")

    for record in records:
        db.delete(record)
        


def create_error(mes: str):
    raise HTTPException(status_code=400, detail={"error": "Validation failed", "message": mes})

IST = timezone(timedelta(hours=5, minutes=30)) 
def format_ist(dt):
        if not dt:
            return None
        dt_ist = dt.replace(tzinfo=timezone.utc).astimezone(IST)
        return dt_ist.strftime("%d %b %Y, %I:%M %p")
    
def encode_ids(event_id: int, user_id: int) -> str:
        combined = f"{event_id}:{user_id}"
        return base64.urlsafe_b64encode(combined.encode()).decode()
    
def decode_ids(token: str) -> tuple[int, int]:
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        event_id, user_id = decoded.split(":")
        return int(event_id), int(user_id)
    except Exception:
        raise ValueError("Invalid token")



import os

async def validate_image_file(file: UploadFile, max_size_mb: int = 10) -> None:
    """
    Validate uploaded image file
    
    Args:
        file: The uploaded file
        max_size_mb: Maximum file size in MB
    """
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Allowed types: JPEG, PNG, WebP"
        )
    
    # Validate file extension
    allowed_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension '{file_extension}'. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Move to end of file
    file_size = file.file.tell()  # Get file size in bytes
    file.file.seek(0)  # Reset to beginning
    
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds {max_size_mb}MB limit. Your file: {file_size / (1024*1024):.2f}MB"
        )


def get_image_url(url:str):
    image = url.replace("\\", "/")
    base_dir = os.path.abspath(os.path.dirname(__file__))  
    # print (os.path.dirname(__file__))
    # print(f"base_dir = {base_dir}")
    project_root = os.path.join(base_dir, "..", "..")  
    # print(f"projecct = {project_root}")
    abs_path = os.path.join(project_root, image)
    # print (type(abs_path))
    abs_path = os.path.normpath(abs_path)  
    # print("Checking path:", abs_path)
    return abs_path.replace("\\", "/")

def raise_exception (status_code, detail: str) -> HTTPException:
    raise HTTPException(status_code=status_code, detail=detail)



def get_url(url: str):
    # Normalize slashes
    image = url.replace("\\", "/")

    # Get absolute path to the project root
    base_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, "..", ".."))

    # Join with project root to form full absolute path
    abs_path = os.path.join(project_root, image.lstrip("/"))
    abs_path = os.path.normpath(abs_path)  # normalize C:\ or / style

    # Convert backslashes to forward slashes for consistency
    return abs_path.replace("\\", "/")

def log_activity(
    db: Session,
    user_id: int,
    activity_type: str,
    title: str,
    description: str,
    event_id: int = None,
    status: str = None,
    amount: float = None
):
    """Log activity to database"""
    activity = ActivityLog(
        user_id=user_id,
        event_id=event_id,
        activity_type=activity_type,
        title=title,
        description=description,
        status=status,
        amount=amount
    )
    db.add(activity)
    db.commit()
    return activity



import os
from tempfile import NamedTemporaryFile
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi import  BackgroundTasks, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, EmailStr


conf = ConnectionConfig(
    MAIL_USERNAME="thigalzhieventmanagement@gmail.com",
    MAIL_PASSWORD="inrl iuyk xagh amhf",
    MAIL_FROM="thigalzhieventmanagement@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,    
    MAIL_SSL_TLS=False,    
    USE_CREDENTIALS=True
)

class EmailSchema(BaseModel):
    email: EmailStr
    subject: str
    message: str

async def auto_email_send(background_tasks: BackgroundTasks, email: EmailSchema):
    message = MessageSchema(
        subject=email.subject,
        recipients=[email.email],
        body=email.message,
        subtype="html"
    )
    
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
    return {"status": "email sent"}




# ---- Function to Send Mail ----
async def send_cancel_email(background_tasks: BackgroundTasks, data: CancelMailSchema):
    message_body = f"""
    Hi {data.name},

    We regret to inform you that {data.event_name} scheduled for {data.event_date} has been cancelled.

    Refund: {data.refund_amount} will be returned to your original payment method within {data.refund_days} days.

    Check refund status: {data.refund_status_url}

    Warmly,
    The Event Team
    """

    message = MessageSchema(
        subject=f"{data.event_name} — Event Cancelled & Refund Info",
        recipients=[data.email],
        body=message_body,
        subtype="plain"  # you can switch to "html" if needed
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
    return {"status": "Email sent successfully"}


async def send_reschedule_email(background_tasks: BackgroundTasks, data: RescheduleMailSchema):
    message_body = f"""
    Hi {data.name},

    We wanted to let you know that {data.event_name} originally scheduled for {data.old_date} 
    has been rescheduled to {data.new_date}.

    If you’re unable to attend on the new date, you can cancel your booking before {data.cancel_before}
    to receive a **full refund of {data.amount}**.

    Warmly,
    The Event Team
    """

    message = MessageSchema(
        subject=f"{data.event_name} — Event Rescheduled Notification",
        recipients=[data.email],
        body=message_body,
        subtype="plain"
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
    return {"status": "Reschedule email sent successfully"}


def send_email(to_mail: str, sub: str, html, background_tasks: BackgroundTasks):
        message = MessageSchema(
            subject=sub,
            recipients=[to_mail],
            body=html,
            subtype='html'
        )
        fm = FastMail(conf)
        background_tasks.add_task(fm.send_message, message)
        return {"message": "Email sent"}