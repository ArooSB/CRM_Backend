from flask import Blueprint, request, jsonify
from backend import db
from backend.models import SalesLead
from flask_jwt_extended import jwt_required

bp = Blueprint('sales_leads', __name__)



@bp.route('/sales_leads', methods=['POST'])
@jwt_required()
def create_sales_lead():
    data = request.get_json()


    if not all(key in data for key in ['customer_id', 'lead_status']):
        return jsonify({"message": "Missing required fields!"}), 400

    new_lead = SalesLead(
        customer_id=data['customer_id'],
        worker_id=data.get('worker_id'),
        lead_status=data['lead_status'],
        lead_source=data.get('lead_source'),
        potential_value=data.get('potential_value')
    )

    db.session.add(new_lead)
    db.session.commit()
    return jsonify({"message": "Sales lead created successfully!"}), 201



@bp.route('/sales_leads', methods=['GET'])
@jwt_required()
def get_sales_leads():
    query = request.args
    leads = SalesLead.query


    if 'lead_status' in query:
        leads = leads.filter(SalesLead.lead_status == query.get('lead_status'))
    if 'lead_source' in query:
        leads = leads.filter(SalesLead.lead_source == query.get('lead_source'))
    if 'min_potential_value' in query and 'max_potential_value' in query:
        min_value = query.get('min_potential_value', type=float)
        max_value = query.get('max_potential_value', type=float)
        leads = leads.filter(SalesLead.potential_value.between(min_value, max_value))

    # Pagination support
    page = query.get('page', 1, type=int)
    per_page = query.get('per_page', 10, type=int)
    leads = leads.paginate(page=page, per_page=per_page, error_out=False)

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
    lead = SalesLead.query.get(id)
    if not lead:
        return jsonify({"message": "Sales lead not found!"}), 404

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
    lead = SalesLead.query.get(id)
    if not lead:
        return jsonify({"message": "Sales lead not found!"}), 404

    db.session.delete(lead)
    db.session.commit()
    return jsonify({"message": "Sales lead deleted successfully!"})
