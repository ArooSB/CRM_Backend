from backend.models import SupportTicket, Worker
from backend import db
from sqlalchemy.exc import SQLAlchemyError


def auto_assign_ticket(ticket):
    """
    Automatically assigns the support ticket to the worker with the least number of tickets.

    Parameters:
        ticket (SupportTicket): The ticket to be assigned.
    """

    try:

        least_busy_worker = Worker.query.outerjoin(
            SupportTicket, SupportTicket.assigned_to == Worker.worker_id
        ).group_by(Worker.worker_id).order_by(
            db.func.count(SupportTicket.ticket_id)
        ).first()

        if not least_busy_worker:
            raise ValueError("No available workers to assign the ticket.")


        ticket.assigned_to = least_busy_worker.worker_id
        db.session.commit()


        print(
            f"Ticket {ticket.ticket_id} assigned to worker {least_busy_worker.first_name} {least_busy_worker.last_name}")

    except SQLAlchemyError as e:

        db.session.rollback()
        print(f"Database error during ticket assignment: {str(e)}")
        raise

    except Exception as e:

        print(f"An error occurred during ticket assignment: {str(e)}")
        raise
