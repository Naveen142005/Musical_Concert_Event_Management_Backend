import os
import uuid
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from app.models.enum import EventStatus
class EventService:
    
    def save_image(self, file):
        upload_dir = "uploads/banners"
        os.makedirs(upload_dir, exist_ok=True)

        file_name = f"{uuid.uuid4().hex}{os.path.splitext(file.filename)[1]}"
        file_path = os.path.join(upload_dir, file_name)

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        return file_path


    def build_event_response(self, event_data, inserted_id: int, user_id: int, payment_id: int):
        event_dict = event_data.dict()

        if not event_dict.get("ticket_enabled"):
            event_dict.pop("platinum_ticket_price", None)
            event_dict.pop("gold_ticket_price", None)
            event_dict.pop("silver_ticket_price", None)

        for facility_field in ["venue_id", "band_id", "decoration_id", "snacks_id", "snacks_count"]:
            if not event_dict.get(facility_field):
                event_dict.pop(facility_field, None)

        response = {
            "id": inserted_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().date(),
            "status": EventStatus.BOOKED,
            "payment_id": payment_id,
            **event_dict,
        }

        if event_dict.get("payment_type") == "Half payment":
            total = event_dict.get("payment_amount", 0)
            pending = total / 2
            response["pending_amount"] = pending

        return jsonable_encoder(response)

    
event_service = EventService()  