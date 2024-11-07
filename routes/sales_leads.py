from flask import Blueprint, request, jsonify, abort
from backend import db
from backend.models import SalesLead
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

bp = Blueprint('sales_leads', __name__)


def validate_sales_lead_data(data):
    required_fields = ['customer_id', 'lead_status']
    if not all(field in data for field in required_fields):
        abort(400, description="Missing required fields: 'customer_id' and 'lead_status'.")


@bp.route('/sales_leads', methods=['POST'])
@jwt_required()
def create_sales_lead():
    data = request.get_json()
    validate_sales_lead_data(data)

    try:
        new_lead = SalesLead(
            customer_id=data['customer_id'],
            worker_id=data.get('worker_id'),
            lead_status=data['lead_status'],
            lead_source=data.get('lead_source'),
            potential_value=data.get('potential_value')
        )
        db.session.add(new_lead)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        error_message = str(e.orig) if e.orig else "Database integrity error."
        return jsonify({"message": "Failed to create sales lead.", "error": error_message}), 500

    return jsonify({
        "message": "Sales lead created successfully!",
        "lead": {
            "lead_id": new_lead.id,
            "customer_id": new_lead.customer_id,
            "worker_id": new_lead.worker_id,
            "lead_status": new_lead.lead_status,
            "lead_source": new_lead.lead_source,
            "potential_value": str(new_lead.potential_value),
            "created_at": new_lead.created_at
        }
    }), 201


@bp.route('/sales_leads', methods=['GET'])
@jwt_required()
def get_sales_leads():
    lead_status = request.args.get('lead_status')
    lead_source = request.args.get('lead_source')
    min_value = request.args.get('min_potential_value', type=float)
    max_value = request.args.get('max_potential_value', type=float)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = SalesLead.query

    if lead_status:
        query = query.filter(SalesLead.lead_status == lead_status)
    if lead_source:
        query = query.filter(SalesLead.lead_source == lead_source)
    if min_value is not None and max_value is not None:
        query = query.filter(SalesLead.potential_value.between(min_value, max_value))

    leads = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'total_leads': leads.total,
        'page': leads.page,
        'per_page': leads.per_page,
        'leads': [{
            'lead_id': l.id,
            'customer_id': l.customer_id,
            'worker_id': l.worker_id,
            'lead_status': l.lead_status,
            'lead_source': l.lead_source,
            'potential_value': str(l.potential_value),
            'created_at': l.created_at
        } for l in leads.items]
    })


@bp.route('/sales_leads/<int:id>', methods=['PUT'])
@jwt_required()
def update_sales_lead(id):
    lead = SalesLead.query.get_or_404(id, description="Sales lead not found.")
    data = request.get_json()

    lead.customer_id = data.get('customer_id', lead.customer_id)
    lead.worker_id = data.get('worker_id', lead.worker_id)
    lead.lead_status = data.get('lead_status', lead.lead_status)
    lead.lead_source = data.get('lead_source', lead.lead_source)
    lead.potential_value = data.get('potential_value', lead.potential_value)

    db.session.commit()

    return jsonify({"message": "Sales lead updated successfully!"})


@bp.route('/sales_leads/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_sales_lead(id):
    lead = SalesLead.query.get_or_404(id, description="Sales lead not found.")

    db.session.delete(lead)
    db.session.commit()

    return jsonify({"message": "Sales lead deleted successfully!"})
