from flask import Blueprint, request, jsonify
from backend import db
from backend.models import Customer
from flask_jwt_extended import jwt_required

bp = Blueprint('customers', __name__)


@bp.route('/customers', methods=['POST'])
@jwt_required()
def create_customer():
    data = request.get_json()


    if not all(key in data for key in ['first_name', 'last_name', 'email']):
        return jsonify({"message": "Missing required fields!"}), 400

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

    return jsonify({"message": "Customer created successfully!"}), 201


@bp.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    name_query = request.args.get('name')

    query = Customer.query

    if name_query:
        query = query.filter((Customer.first_name.ilike(f'%{name_query}%')) |
                             (Customer.last_name.ilike(f'%{name_query}%')))

    customers = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'total_customers': customers.total,
        'page': customers.page,
        'per_page': customers.per_page,
        'customers': [{
            'customer_id': c.id,
            'first_name': c.first_name,
            'last_name': c.last_name,
            'email': c.email,
            'phone': c.phone,
            'company': c.company,
            'address': c.address
        } for c in customers.items]
    })


@bp.route('/customers/<int:id>', methods=['PUT'])
@jwt_required()
def update_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({"message": "Customer not found!"}), 404

    data = request.get_json()


    customer.first_name = data.get('first_name', customer.first_name)
    customer.last_name = data.get('last_name', customer.last_name)
    customer.email = data.get('email', customer.email)
    customer.phone = data.get('phone', customer.phone)
    customer.company = data.get('company', customer.company)
    customer.address = data.get('address', customer.address)

    db.session.commit()

    return jsonify({"message": "Customer updated successfully!"})


@bp.route('/customers/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({"message": "Customer not found!"}), 404

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": "Customer deleted successfully!"})
