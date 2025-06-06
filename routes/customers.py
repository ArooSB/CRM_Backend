from flask import Blueprint, request, jsonify, abort
from backend import db
from backend.models import Customer
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

bp = Blueprint('customers', __name__)


def validate_customer_data(data, check_email=True):
    required_fields = ['first_name', 'last_name', 'email']
    if not all(field in data for field in required_fields):
        abort(400, description="Missing required fields: 'first_name', 'last_name', and 'email'.")

    if check_email:
        if not isinstance(data.get('email'), str) or '@' not in data.get('email'):
            abort(400, description="Invalid email format.")


@bp.route('/customers', methods=['POST'])
@jwt_required()
def create_customer():
    data = request.get_json()
    validate_customer_data(data)

    try:
        new_customer = Customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            company=data.get('company'),
            address=data.get('address')
        )
        db.session.add(new_customer)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Email already exists."}), 409

    return jsonify({"message": "Customer created successfully!", "customer_id": new_customer.id}), 201



@bp.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    name_query = request.args.get('name', '')


    query = Customer.query
    if name_query:
        query = query.filter(or_(
            Customer.first_name.ilike(f'%{name_query}%'),
            Customer.last_name.ilike(f'%{name_query}%')
        ))


    customers = query.paginate(page=page, per_page=per_page, error_out=False)

    response = {
        'total_customers': customers.total,
        'page': customers.page,
        'per_page': customers.per_page,
        'total_pages': customers.pages,
        'has_next': customers.has_next,
        'has_prev': customers.has_prev,
        'customers': [{
            'customer_id': c.id,
            'first_name': c.first_name,
            'last_name': c.last_name,
            'email': c.email,
            'phone': c.phone,
            'company': c.company,
            'address': c.address
        } for c in customers.items]
    }

    return jsonify(response), 200



@bp.route('/customers/<int:id>', methods=['PUT'])
@jwt_required()
def update_customer(id):
    customer = Customer.query.get_or_404(id, description="Customer not found.")
    data = request.get_json()

    # Validate email format if email is being updated
    if 'email' in data and (not isinstance(data['email'], str) or '@' not in data['email']):
        abort(400, description="Invalid email format.")

    # Update fields only if provided in the request
    customer.first_name = data.get('first_name', customer.first_name)
    customer.last_name = data.get('last_name', customer.last_name)
    customer.email = data.get('email', customer.email)
    customer.phone = data.get('phone', customer.phone)
    customer.company = data.get('company', customer.company)
    customer.address = data.get('address', customer.address)


    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Email already exists."}), 409

    return jsonify({"message": "Customer updated successfully!"}), 200



@bp.route('/customers/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_customer(id):
    customer = Customer.query.get_or_404(id, description="Customer not found.")

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": "Customer deleted successfully!"}), 200



@bp.route('/customers/<int:id>', methods=['GET'])
@jwt_required()
def get_customer(id):
    customer = Customer.query.get_or_404(id, description="Customer not found.")
    return jsonify({
        'customer_id': customer.id,
        'first_name': customer.first_name,
        'last_name': customer.last_name,
        'email': customer.email,
        'phone': customer.phone,
        'company': customer.company,
        'address': customer.address
    }), 200
