from flask import Blueprint, request, jsonify, abort
from backend import db
from backend.models import SupportTicket, Worker, Customer
from services.auto_assignment import auto_assign_ticket
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

bp = Blueprint('support_tickets', __name__)

# Validation function for ticket data
def validate_ticket_data(data, required_fields, valid_statuses):
    """Validates that all required fields are in the request data and checks for valid statuses."""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        abort(400,
              description=f"Missing required fields: {', '.join(missing_fields)}.")

    if 'ticket_status' in data and data['ticket_status'] not in valid_statuses:
        abort(400,
              description=f"Invalid ticket status. Allowed values: {', '.join(valid_statuses)}.")

# POST route to create a support ticket
@bp.route('/support_tickets', methods=['POST'])
@jwt_required()
def create_support_ticket():
    """Create a new support ticket and auto-assign it to an available worker."""
    data = request.get_json()
    required_fields = ['customer_id', 'created_by', 'ticket_subject']
    valid_statuses = ['Open', 'Close', 'In Process']

    validate_ticket_data(data, required_fields, valid_statuses)

    # Check if the customer exists
    if not db.session.query(Customer).filter_by(id=data['customer_id']).first():
        return jsonify({"message": "Customer not found."}), 400

    # Check if the worker exists (if provided)
    if data.get('created_by') and not db.session.query(Worker).filter_by(id=data['created_by']).first():
        return jsonify({"message": "Worker not found."}), 400

    try:
        # Create a new support ticket
        new_ticket = SupportTicket(
            customer_id=data['customer_id'],
            created_by=data['created_by'],
            ticket_subject=data['ticket_subject'],
            ticket_description=data.get('ticket_description', ''),
            ticket_status=data.get('ticket_status', 'Open')  # Default to 'Open' if no status provided
        )
        db.session.add(new_ticket)
        db.session.commit()

        # Auto-assign the ticket (if needed)
        auto_assign_ticket(new_ticket)

    except IntegrityError:
        db.session.rollback()
        return jsonify({
                           "message": "Failed to create support ticket due to a database error."
                       }), 500

    return jsonify({
        "message": "Support ticket created successfully and assigned!",
        "ticket_id": new_ticket.id  # Use the correct primary key field
    }), 201

# GET route to retrieve all or filtered support tickets
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

    # Handle pagination
    page = query.get('page', 1, type=int)
    per_page = query.get('per_page', 10, type=int)
    tickets = tickets.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'total_tickets': tickets.total,
        'page': tickets.page,
        'per_page': tickets.per_page,
        'tickets': [{
            'ticket_id': t.id,
            'customer_id': t.customer_id,
            'created_by': t.created_by,
            'assigned_to': t.assigned_to,
            'ticket_subject': t.ticket_subject,
            'ticket_description': t.ticket_description,
            'ticket_status': t.ticket_status,
            'created_at': t.created_at
        } for t in tickets.items]
    })

# PUT route to update an existing support ticket
@bp.route('/support_tickets/<int:id>', methods=['PUT'])
@jwt_required()
def update_support_ticket(id):
    """Update an existing support ticket."""
    ticket = SupportTicket.query.get_or_404(id, description="Support ticket not found.")
    data = request.get_json()
    valid_statuses = ['Open', 'Close', 'In Process']

    if 'ticket_status' in data and data['ticket_status'] not in valid_statuses:
        abort(400, description=f"Invalid ticket status. Allowed values: {', '.join(valid_statuses)}.")

    # Update fields, preserving existing values where no new data is provided
    ticket.customer_id = data.get('customer_id', ticket.customer_id)
    ticket.assigned_to = data.get('assigned_to', ticket.assigned_to)
    ticket.ticket_subject = data.get('ticket_subject', ticket.ticket_subject)
    ticket.ticket_description = data.get('ticket_description', ticket.ticket_description)
    ticket.ticket_status = data.get('ticket_status', ticket.ticket_status)

    db.session.commit()

    return jsonify({"message": "Support ticket updated successfully!"})

# DELETE route to remove an existing support ticket
@bp.route('/support_tickets/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_support_ticket(id):
    """Delete an existing support ticket."""
    ticket = SupportTicket.query.get_or_404(id, description="Support ticket not found.")

    db.session.delete(ticket)
    db.session.commit()

    return jsonify({"message": "Support ticket deleted successfully!"})
