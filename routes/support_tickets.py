from flask import Blueprint, request, jsonify, abort
from backend import db
from backend.models import SupportTicket
from services.auto_assignment import auto_assign_ticket
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

bp = Blueprint('support_tickets', __name__)

def validate_ticket_data(data, required_fields):
    if not all(field in data for field in required_fields):
        abort(400, description=f"Missing required fields: {', '.join(required_fields)}.")


@bp.route('/support_tickets', methods=['POST'])
@jwt_required()
def create_support_ticket():
    """Create a new support ticket and auto-assign it."""
    data = request.get_json()
    required_fields = ['customer_id', 'created_by', 'ticket_subject', 'ticket_status']
    validate_ticket_data(data, required_fields)

    try:
        new_ticket = SupportTicket(
            customer_id=data['customer_id'],
            created_by=data['created_by'],
            ticket_subject=data['ticket_subject'],
            ticket_description=data.get('ticket_description', ''),
            ticket_status=data['ticket_status']
        )

        db.session.add(new_ticket)
        db.session.commit()


        auto_assign_ticket(new_ticket)
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Failed to create support ticket due to a database error."}), 500

    return jsonify({
        "message": "Support ticket created successfully and assigned!",
        "ticket_id": new_ticket.ticket_id
    }), 201


@bp.route('/support_tickets', methods=['GET'])
@jwt_required()
def get_support_tickets():
    """Retrieve all support tickets or filter by specific fields."""
    query = request.args


    tickets = SupportTicket.query


    if 'ticket_status' in query:
        tickets = tickets.filter(SupportTicket.ticket_status == query.get('ticket_status'))
    if 'customer_id' in query:
        tickets = tickets.filter(SupportTicket.customer_id == query.get('customer_id'))


    page = query.get('page', 1, type=int)
    per_page = query.get('per_page', 10, type=int)
    tickets = tickets.paginate(page=page, per_page=per_page, error_out=False)


    return jsonify({
        'total_tickets': tickets.total,
        'page': tickets.page,
        'per_page': tickets.per_page,
        'tickets': [{
            'ticket_id': t.ticket_id,
            'customer_id': t.customer_id,
            'created_by': t.created_by,
            'assigned_to': t.assigned_to,
            'ticket_subject': t.ticket_subject,
            'ticket_description': t.ticket_description,
            'ticket_status': t.ticket_status,
            'created_at': t.created_at
        } for t in tickets.items]
    })


@bp.route('/support_tickets/<int:id>', methods=['PUT'])
@jwt_required()
def update_support_ticket(id):
    """Update an existing support ticket."""
    ticket = SupportTicket.query.get_or_404(id, description="Support ticket not found.")
    data = request.get_json()


    ticket.customer_id = data.get('customer_id', ticket.customer_id)
    ticket.assigned_to = data.get('assigned_to', ticket.assigned_to)
    ticket.ticket_subject = data.get('ticket_subject', ticket.ticket_subject)
    ticket.ticket_description = data.get('ticket_description', ticket.ticket_description)
    ticket.ticket_status = data.get('ticket_status', ticket.ticket_status)

    db.session.commit()

    return jsonify({"message": "Support ticket updated successfully!"})


@bp.route('/support_tickets/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_support_ticket(id):
    """Delete an existing support ticket."""
    ticket = SupportTicket.query.get_or_404(id, description="Support ticket not found.")

    db.session.delete(ticket)
    db.session.commit()

    return jsonify({"message": "Support ticket deleted successfully!"})
