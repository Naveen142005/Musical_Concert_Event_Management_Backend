from datetime import datetime, time

import yagmail
from app.database.connection import SessionLocal
from app.models.escrow import Escrow
from app.models.events import Event
from app.models.bookings import Bookings
from app.models.enum import ESCROWSTATUS, EventStatus, PaymentStatus
from app.models.payment import Payment
from app.models.tickets import Tickets
from app.models.user import User
from app.services.feedback import feedback_service
from fastapi import BackgroundTasks


async def update_event_status():
    db = SessionLocal()
    try:
        now = datetime.now()
        today = now.date()
        current_time = now.time()

        events = db.query(Event).all()
        print("Event status update started")

        for event in events:
            if event.status in [EventStatus.CANCELLED, EventStatus.COMPLETED]:
                continue

            if event.event_date == today:
                slot = event.slot.lower()
                print(f"Updating {event.name} ({slot})")

                # Morning
                if slot == "morning":
                    if current_time < time(6, 0):
                        continue
                    elif time(6, 0) <= current_time <= time(12, 0):
                        event.status = EventStatus.ONGOING
                    else:
                        event.status = EventStatus.COMPLETED

                # Afternoon
                elif slot == "afternoon":
                    if current_time < time(12, 0):
                        continue
                    elif time(12, 0) <= current_time <= time(18, 0):
                        event.status = EventStatus.ONGOING
                    else:
                        event.status = EventStatus.COMPLETED

                # Night
                elif slot == "night":
                    if current_time < time(18, 0):
                        continue
                    elif time(18, 0) <= current_time <= time(23, 59):
                        event.status = EventStatus.ONGOING
                    else:
                        event.status = EventStatus.COMPLETED

                # Send feedback email when completed
                if event.status == EventStatus.COMPLETED:
                    print(f"Sending feedback email for event {event.id}")
                    
                    # Create background tasks instance
                    background_tasks = BackgroundTasks()
                    
                    # Send to organizer
                    try:
                        res = await feedback_service.send_feedback(
                            id=event.id,
                            user_id=event.user_id,
                            db=db,
                            background_tasks=background_tasks,
                            f = True
                        )
                        print(res)
                        print(f" Feedback sent to organizer (user_id: {event.user_id})")
                    except Exception as e:
                        print(f" Failed to send organizer feedback: {e}")

                    # Send to audience if tickets enabled
                    if event.ticket_enabled:
                        bookings = db.query(Bookings).filter(Bookings.event_id == event.id).all()
                        for booking in bookings:
                            try:
                                bg_tasks = BackgroundTasks()
                                await feedback_service.send_feedback(
                                    id=booking.id,
                                    user_id=booking.user_id,
                                    db=db,
                                    background_tasks=bg_tasks,
                                    f = True
                                )
                                print(f" Feedback sent to audience (user_id: {booking.user_id})")
                            except Exception as e:
                                print(f" Failed to send audience feedback: {e}")

        db.commit()
        print(f" [{now.strftime('%H:%M:%S')}] Event statuses updated successfully")

    except Exception as e:
        db.rollback()
        print(f" Error: {e}")
    finally:
        db.close()



async def check_pending_payments():
    """Check for events with pending payments and send reminders or cancel"""
    db = SessionLocal()
    try:
        now = datetime.now()
        today = now.date()

        # Get events with pending payments
        events = db.query(Event).filter(
            Event.status.in_([EventStatus.BOOKED, EventStatus.UPCOMING]),
            Event.event_date >= today
        ).all()

        for event in events:
            # Get payment details
            payment = db.query(Payment).filter(Payment.event_id == event.id).first()
            
            if not payment:
                continue
            
            # Check if payment is pending
            if payment.status == PaymentStatus.PENDING:
                days_until_event = (event.event_date - today).days
                user = db.query(User).filter(User.id == event.user_id).first()
                
                # Event date passed - CANCEL EVENT
                if days_until_event < 0:
                    event.status = EventStatus.CANCELLED
                    payment.status = PaymentStatus.FAILED
                    db.commit()
                    
                    # Send cancellation email
                    send_cancellation_email(user.email, event.name, payment.payment_amount)
                    print(f" Event {event.id} cancelled - Payment not completed")
                
                # Send reminders at specific intervals
                elif days_until_event == 7:
                    send_payment_reminder(user.email, event.name, event.event_date, payment.payment_amount, "7 days")
                    print(f" 7-day payment reminder sent for event {event.id}")
                
                elif days_until_event == 3:
                    send_payment_reminder(user.email, event.name, event.event_date, payment.payment_amount, "3 days")
                    print(f" 3-day payment reminder sent for event {event.id}")
                
                elif days_until_event == 1:
                    send_payment_reminder(user.email, event.name, event.event_date, payment.payment_amount, "1 day", urgent=True)
                    print(f"URGENT payment reminder sent for event {event.id}")

        db.commit()
        print(f" [{now.strftime('%H:%M:%S')}] Payment check completed")

    except Exception as e:
        db.rollback()
        print(f" Payment check error: {e}")
    finally:
        db.close()


def send_payment_reminder(email: str, event_name: str, event_date, pending_amount: float, time_left: str, urgent: bool = False):
    """Send payment reminder email"""
    
    subject = f"{'URGENT: ' if urgent else ''}Payment Reminder - {event_name}"
    
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="{'background-color: #ff4444; color: white;' if urgent else 'background-color: #f59e0b; color: white;'} padding: 20px; text-align: center;">
                <h2>{'URGENT PAYMENT REMINDER' if urgent else ' Payment Reminder'}</h2>
            </div>
            
            <div style="padding: 20px;">
                <p>Hello,</p>
                
                <p>This is a reminder that you have a <strong>pending payment</strong> for your event:</p>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Event Name:</strong> {event_name}</p>
                    <p style="margin: 5px 0;"><strong>Event Date:</strong> {event_date}</p>
                    <p style="margin: 5px 0;"><strong>Pending Amount:</strong> Rs. {pending_amount:,.2f}</p>
                    <p style="margin: 5px 0;"><strong>Time Remaining:</strong> {time_left}</p>
                </div>
                
                <div style="background-color: {'#fee2e2' if urgent else'#fef3c7'}; padding: 15px; border-radius: 8px; border-left: 4px solid {'#dc2626' if urgent else '#f59e0b'};">
                    <p style="margin: 0;"><strong>{' IMPORTANT:' if urgent else 'Note:'}</strong> 
                    {'Your event will be automatically cancelled if payment is not completed before the event date!' if urgent else 'Please complete your payment to confirm your event booking.'}</p>
                </div>
                
                <p style="text-align: center; margin-top: 30px;">
                    <a href="http://localhost:8000/payments/complete" style="
                        display: inline-block;
                        background-color: #10b981;
                        color: white;
                        padding: 12px 30px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;">
                        Complete Payment Now
                    </a>
                </p>
                
                <p>If you have any questions, please contact us at thigalzhieventmanagement@gmail.com</p>
                
                <p>Best regards,<br/>
                <strong>Thigalzhi® Event Management Team</strong></p>
            </div>
        </body>
    </html>
    """
    
    try:
        my_email = 'thigalzhieventmanagement@gmail.com'
        password = 'inrl iuyk xagh amhf'
        yag = yagmail.SMTP(user=my_email, password=password)
        yag.send(to=email, subject=subject, contents=html)
    except Exception as e:
        print(f"Failed to send reminder email: {e}")


def send_cancellation_email(email: str, event_name: str, refund_amount: float):
    """Send event cancellation email"""
    
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="background-color: #dc2626; color: white; padding: 20px; text-align: center;">
                <h2>Event Cancelled</h2>
            </div>
            
            <div style="padding: 20px;">
                <p>Hello,</p>
                
                <p>We regret to inform you that your event <strong>{event_name}</strong> has been <strong>cancelled</strong> due to incomplete payment.</p>
                
                <div style="background-color: #fee2e2; padding: 15px; border-radius: 8px; border-left: 4px solid #dc2626; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Reason:</strong> Payment not completed before event date</p>
                </div>
                
                <p>Your advance payment of <strong>Rs. {refund_amount:,.2f}</strong> will be refunded within 7-10 business days.</p>
                
                <p>If you wish to rebook this event, please contact us at thigalzhieventmanagement@gmail.com</p>
                
                <p>Best regards,<br/>
                <strong>Thigalzhi® Event Management Team</strong></p>
            </div>
        </body>
    </html>
    """
    
    try:
        my_email = 'thigalzhieventmanagement@gmail.com'
        password = 'inrl iuyk xagh amhf'
        yag = yagmail.SMTP(user=my_email, password=password)
        yag.send(to=email, subject=f"Event Cancelled - {event_name}", contents=html)
    except Exception as e:
        print(f"Failed to send cancellation email: {e}")

async def update_escrow_amount():
    """Calculate ticket revenue and update escrow with 80% released amount"""
    db = SessionLocal()
    try:
        # Get all events with tickets enabled and completed status
        events = db.query(Event).filter(
            Event.ticket_enabled == True,
            Event.status == EventStatus.COMPLETED
        ).all()

        for event in events:
            # Check if escrow already exists for this event
            escrow = db.query(Escrow).filter(Escrow.event_id == event.id).first()
            
            if escrow and escrow.status == ESCROWSTATUS.RELEASED:
                continue  # Already released, skip
            
            # Calculate total ticket revenue
            tickets = db.query(Tickets).filter(Tickets.event_id == event.id).all()
            
            total_ticket_revenue = 0
            for ticket in tickets:
                total_ticket_revenue += ticket.booked_ticket * ticket.price
            
            # Calculate 80% release amount
            release_amount = total_ticket_revenue * 0.80
            
            # Create or update escrow
            if escrow:
                escrow.total_amount = total_ticket_revenue
                escrow.released_amount = release_amount
                escrow.status = ESCROWSTATUS.RELEASED
            else:
                escrow = Escrow(
                    event_id=event.id,
                    user_id=event.user_id,
                    total_amount=total_ticket_revenue,
                    released_amount=release_amount,
                    status=ESCROWSTATUS.RELEASED
                )
                db.add(escrow)
            
            db.commit()
            print(f" Escrow updated for event {event.id}: Total={total_ticket_revenue}, Released={release_amount}")

        print(f" Escrow update completed")

    except Exception as e:
        db.rollback()
        print(f"Escrow update error: {e}")
    finally:
        db.close()


def start_scheduler():
    from apscheduler.schedulers.background import BackgroundScheduler
    import asyncio
    
    def run_update():
        asyncio.run(update_event_status())
    
    def run_payment_check():
        asyncio.run(check_pending_payments())
    
    
    def run_escrow_update():
        asyncio.run(update_escrow_amount())
        
    scheduler = BackgroundScheduler()
    
    scheduler.add_job(run_payment_check, 'cron', hour=9, minute=0)
    scheduler.add_job(run_update, 'cron', hour='6,12,18,23', minute=1)
    scheduler.add_job(run_escrow_update, 'cron', hour=23, minute=0)
    scheduler.start()
    
    print("Scheduler started.............................................")
    return scheduler

