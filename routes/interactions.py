from flask import Blueprint, request, jsonify
from backend import db
from backend.models import Interaction
from flask_jwt_extended import jwt_required

bp = Blueprint('interactions', __name__)


@bp.route('/interactions', methods=['POST'])
@jwt_required()
def create_interaction():
    data = request.get_json()


    if not all(key in data for key in ['customer_id', 'interaction_type', 'interaction_date']):
        return jsonify({"message": "Missing required fields!"}), 400

    new_interaction = Interaction(
        customer_id=data['customer_id'],
        worker_id=data.get('worker_id'),
        interaction_type=data['interaction_type'],
        interaction_date=data['interaction_date'],
        interaction_notes=data.get('interaction_notes'),
        communication_summary=data.get('communication_summary')
    )

    db.session.add(new_interaction)
    db.session.commit()

    return jsonify({"message": "Interaction created successfully!"}), 201


@bp.route('/interactions', methods=['GET'])
@jwt_required()
def get_interactions():
    query = request.args
    interactions = Interaction.query


    if 'status' in query:
        status_filter = query.get('status')
        interactions = interactions.filter(Interaction.status == status_filter)

    if 'interaction_id' in query:
        interaction_id = query.get('interaction_id')
        interactions = interactions.filter(Interaction.id == interaction_id)


    page = query.get('page', 1, type=int)
    per_page = query.get('per_page', 10, type=int)
    interactions = interactions.paginate(page=page, per_page=per_page, error_out=False)

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
    interaction = Interaction.query.get(id)
    if not interaction:
        return jsonify({"message": "Interaction not found!"}), 404

    data = request.get_json()

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
    interaction = Interaction.query.get(id)
    if not interaction:
        return jsonify({"message": "Interaction not found!"}), 404

    db.session.delete(interaction)
    db.session.commit()

    return jsonify({"message": "Interaction deleted successfully!"})
