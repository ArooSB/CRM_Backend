from backend.models import SupportTicket, Worker
from backend import db


def auto_assign_ticket(ticket):

    least_busy_worker = Worker.query.outerjoin(SupportTicket,
                                               SupportTicket.assigned_to == Worker.worker_id) \
        .group_by(Worker.worker_id) \
        .order_by(db.func.count(SupportTicket.ticket_id)).first()

    ticket.assigned_to = least_busy_worker.worker_id
    db.session.commit()
    print(
        f"Ticket {ticket.ticket_id} assigned to {least_busy_worker.first_name}")
