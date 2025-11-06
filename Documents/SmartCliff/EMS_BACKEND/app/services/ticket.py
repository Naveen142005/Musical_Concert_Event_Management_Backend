from pytest import Session

from app.schemas.event import EventBase
from app.utils.common import create_error, get_rows, insert_data, insert_data_flush
from app.models.tickets import Tickets

class TicketService:
    def add_ticket_details(self, event_data, db: Session, eventId: int):
        if eventId <= 0:
            create_error('Provide valid event Id')
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
    
    def get_ticket_details_for_event(self ,db, event_id: int):
        if event_id <= 0:
            create_error('Provide valid event Id')
      
        ticket_rows: list[Tickets] = get_rows(db, Tickets, event_id=event_id)
        if not ticket_rows:
            return []

        ticket_list = []
        for ticket in ticket_rows:
            ticket_dict = {
                "ticket_type_name": ticket.ticket_type_name,
                "price": ticket.price,
                "booked_ticket": ticket.booked_ticket,
                "available_count": ticket.available_counts
            }
            ticket_list.append(ticket_dict)

        return ticket_list


    def get_booked_ticket_details(self, db, event_id: int):
        if event_id <= 0:
            create_error('Provide valid event Id')
        ticket_rows: list[Tickets] = get_rows(db, Tickets, event_id=event_id)
        if not ticket_rows:
            create_error("For this event ticket enabled is False. ")

        ticket_list = []
        total_event_earning = 0

        for ticket in ticket_rows:
            total_earning = ticket.booked_ticket * ticket.price
            total_event_earning += total_earning

            ticket_dict = {
                "ticket_type_name": ticket.ticket_type_name,
                "price": ticket.price,
                "booked_ticket": ticket.booked_ticket,
                "available_count": ticket.available_counts,
                "total_earning": total_earning
            }
            ticket_list.append(ticket_dict)

        return {
            "total_event_earning": total_event_earning,
            "tickets": ticket_list
        }
        
    def get_available_tickets_by_event(_, event_id: int, db: Session):
        tickets = (
            db.query(Tickets)
            .filter(Tickets.event_id == event_id)
            .all()
        )

        if not tickets:
           create_error('Ticket deatils not found')

        ticket_list = [
            {
                "ticket_type": ticket.ticket_type_name,
                "available_count": ticket.available_counts
            }
            for ticket in tickets
        ]

        total_available = sum(ticket["available_count"] for ticket in ticket_list)

        return {
            "event_id": event_id,
            "total_available": total_available,
            "tickets": ticket_list
        }


ticket_service = TicketService()