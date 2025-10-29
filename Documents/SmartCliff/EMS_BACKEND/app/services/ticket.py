from pytest import Session

from app.schemas.event import EventBase
from app.utils.common import insert_data, insert_data_flush
from app.models.tickets import Tickets

class TicketService:
    def add_ticket_details(self, event_data, db: Session, eventId: int):
        ticket_types = [
            ("Platinum", event_data.platinum_ticket_price, event_data.platinum_ticket_count),
            ("Gold", event_data.gold_ticket_price, event_data.gold_ticket_count),
            ("Silver", event_data.silver_ticket_price, event_data.silver_ticket_count),
        ]

        for name, price, count in ticket_types:
            if price and count:
                insert_data(
                    db,
                    Tickets,
                    event_id = eventId,
                    ticket_type_name=name,
                    price=price,
                    available_counts=count
                )
        return {"Mes" : "Added"}

ticket_service = TicketService()