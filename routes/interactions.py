from flask import Blueprint, request, jsonify, abort
from backend import db
from backend.models import Interaction, Customer, Worker
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime

bp = Blueprint('interactions', __name__)


def validate_interaction_data(data):
    required_fields = ['customer_id', 'interaction_type', 'interaction_date']
    if not all(field in data for field in required_fields):
        abort(400, description="Missing required fields: 'customer_id', 'interaction_type', and 'interaction_date'.")

    # Check if customer exists
    if not Customer.query.get(data['customer_id']):
        abort(404, description="Customer with given ID does not exist.")

    # Check if worker exists (if provided)
    if data.get('worker_id') and not Worker.query.get(data['worker_id']):
        abort(404, description="Worker with given ID does not exist.")


    try:
        datetime.strptime(data['interaction_date'], '%Y-%m-%d')
    except ValueError:
        abort(400, description="Invalid date format. Use 'YYYY-MM-DD'.")


@bp.route('/interactions', methods=['POST'])
@jwt_required()
def create_interaction():
    data = request.get_json()
    validate_interaction_data(data)

    try:
        new_interaction = Interaction(
            customer_id=data['customer_id'],
            worker_id=data.get('worker_id'),
            interaction_type=data['interaction_type'],
            interaction_date=data['interaction_date'],
            interaction_notes=data.get('interaction_notes', ''),
            communication_summary=data.get('communication_summary', '')
        )
        db.session.add(new_interaction)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Database integrity error. Please check the provided data."}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "Failed to create interaction due to a database error."}), 500

    return jsonify({
        "message": "Interaction created successfully!",
        "interaction_id": new_interaction.id
    }), 201


@bp.route('/interactions', methods=['GET'])
@jwt_required()
def get_interactions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status_filter = request.args.get('status')
    customer_id = request.args.get('customer_id', type=int)

    query = Interaction.query

    if status_filter:
        query = query.filter(Interaction.status == status_filter)

    if customer_id:
        query = query.filter(Interaction.customer_id == customer_id)

    interactions = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'total_interactions': interactions.total,
        'page': interactions.page,
        'per_page': interactions.per_page,
        'interactions': [{
            'interaction_id': i.id,
            'customer_id': i.customer_id,
            'worker_id': i.worker_id,
            'interaction_type': i.interaction_type,
            'interaction_date': i.interaction_date,
            'interaction_notes': i.interaction_notes,
            'communication_summary': i.communication_summary,
            'created_at': i.created_at
        } for i in interactions.items]
    })


@bp.route('/interactions/<int:id>', methods=['PUT'])
@jwt_required()
def update_interaction(id):
    interaction = Interaction.query.get_or_404(id, description="Interaction not found.")
    data = request.get_json()


    if 'customer_id' in data and not Customer.query.get(data['customer_id']):
        abort(404, description="Customer with given ID does not exist.")
    if 'worker_id' in data and data['worker_id'] and not Worker.query.get(data['worker_id']):
        abort(404, description="Worker with given ID does not exist.")


    interaction.customer_id = data.get('customer_id', interaction.customer_id)
    interaction.worker_id = data.get('worker_id', interaction.worker_id)
    interaction.interaction_type = data.get('interaction_type', interaction.interaction_type)
    interaction.interaction_date = data.get('interaction_date', interaction.interaction_date)
    interaction.interaction_notes = data.get('interaction_notes', interaction.interaction_notes)
    interaction.communication_summary = data.get('communication_summary', interaction.communication_summary)

    db.session.commit()

    return jsonify({"message": "Interaction updated successfully!"})


@bp.route('/interactions/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_interaction(id):
    interaction = Interaction.query.get_or_404(id, description="Interaction not found.")

    db.session.delete(interaction)
    db.session.commit()

    return jsonify({"message": "Interaction deleted successfully!"})
