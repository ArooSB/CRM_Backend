from flask import Blueprint, request, jsonify, current_app
from backend import db
from backend.models import Worker
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from datetime import datetime, timedelta

bp = Blueprint('workers', __name__)

# Decorator to restrict access based on worker role

"""
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_worker, *args, **kwargs):
            if current_worker.position != role:
                return jsonify({"message": "You do not have permission to perform this action!"}), 403
            return f(current_worker, *args, **kwargs)
        return decorated_function
    return decorator

"""


# Decorator to restrict access based on worker role
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_worker = kwargs.get('current_worker', None)
            if not current_worker:
                return jsonify({"message": "Authorization required!"}), 401

            if current_worker.position != role:
                return jsonify({
                                   "message": "You do not have permission to perform this action!"}), 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Decorator to require a valid JWT token for access
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            token = auth_header.split(" ")[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_worker = Worker.query.get(data['sub'])
            if not current_worker:
                return jsonify({"message": "Worker not found!"}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 403

        # Inject `current_worker` into kwargs
        kwargs['current_worker'] = current_worker
        return f(*args, **kwargs)

    return decorated


"""
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            token = auth_header.split(" ")[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_worker = Worker.query.get(data['sub'])
            if not current_worker:
                return jsonify({"message": "Worker not found!"}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 403

        return f(current_worker, *args, **kwargs)
    return decorated
"""


@bp.route('/workers', methods=['POST'])
@token_required
@role_required('admin')
def create_worker(current_worker):
    """Create a new worker account. Only accessible by admin."""
    data = request.get_json()
    required_fields = ['username', 'password', 'first_name', 'last_name', 'position', 'email']
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields!"}), 400

    if Worker.query.filter((Worker.username == data['username']) | (Worker.email == data['email'])).first():
        return jsonify({"message": "Username or email already exists!"}), 400

    new_worker = Worker(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        first_name=data['first_name'],
        last_name=data['last_name'],
        position=data['position'],
        email=data['email'],
        created_at=datetime.utcnow()
    )
    db.session.add(new_worker)
    db.session.commit()

    return jsonify({"message": "Worker created successfully!"}), 201

@bp.route('/workers', methods=['GET'])
@token_required
@role_required('admin')
def get_workers(current_worker):
    """Retrieve all workers. Accessible only to admins."""
    workers = Worker.query.all()
    result = [{
        'worker_id': w.id,
        'username': w.username,
        'first_name': w.first_name,
        'last_name': w.last_name,
        'position': w.position,
        'email': w.email,
        'created_at': w.created_at.isoformat()
    } for w in workers]
    return jsonify(result), 200

@bp.route('/workers/login', methods=['POST'])
def login_worker():
    """Authenticate a worker and return a JWT."""
    data = request.get_json()
    if not all(field in data for field in ['username', 'password']):
        return jsonify({"message": "Missing username or password!"}), 400

    worker = Worker.query.filter_by(username=data['username']).first()
    if not worker or not check_password_hash(worker.password_hash, data['password']):
        return jsonify({"message": "Invalid credentials!"}), 401

    token = jwt.encode({
        'sub': worker.id,
        'exp': datetime.utcnow() + timedelta(hours=12)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({"token": token, "message": "Worker logged in successfully!"}), 200

@bp.route('/workers/<int:id>', methods=['PUT'])
@token_required
@role_required('admin')
def update_worker(current_worker, id):
    """Update an existing worker's information. Admin only."""
    worker = Worker.query.get_or_404(id)
    data = request.get_json()

    worker.first_name = data.get('first_name', worker.first_name)
    worker.last_name = data.get('last_name', worker.last_name)
    worker.position = data.get('position', worker.position)
    worker.email = data.get('email', worker.email)

    db.session.commit()
    return jsonify({"message": "Worker updated successfully!"}), 200

@bp.route('/workers/password/<int:id>', methods=['PUT'])
@token_required
def update_worker_password(current_worker, id):
    """Update only the password for the worker."""
    if current_worker.id != id and current_worker.position != 'admin':
        return jsonify({"message": "You can only update your own password!"}), 403

    worker = Worker.query.get_or_404(id)
    data = request.get_json()

    if 'password' not in data:
        return jsonify({"message": "Password is required!"}), 400

    worker.password_hash = generate_password_hash(data['password'])
    db.session.commit()
    return jsonify({"message": "Password updated successfully!"}), 200

@bp.route('/workers/<int:id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_worker(current_worker, id):
    """Delete a worker's account."""
    worker = Worker.query.get_or_404(id)
    if current_worker.id == worker.id:
        return jsonify({"message": "You cannot delete your own account!"}), 403

    db.session.delete(worker)
    db.session.commit()
    return jsonify({"message": "Worker deleted successfully!"}), 200

@bp.route('/workers/me', methods=['GET'])
@token_required
def get_my_profile(current_worker):
    """Get the current worker's profile."""
    return jsonify({
        'worker_id': current_worker.id,
        'username': current_worker.username,
        'first_name': current_worker.first_name,
        'last_name': current_worker.last_name,
        'position': current_worker.position,
        'email': current_worker.email,
        'created_at': current_worker.created_at.isoformat()
    }), 200

# Helper function to create an admin worker if none exists
def create_admin():
    """
    Creates an admin worker if none exists.
    Admin username and password are set as 'admin' by default but should be changed.
    """
    admin_worker = Worker.query.filter_by(username='admin').first()
    if not admin_worker:
        try:
            # Define the new admin credentials
            admin_worker = Worker(
                username='admin',
                password_hash=generate_password_hash('admin_password'),  # Secure password for production
                first_name='System',
                last_name='Administrator',
                position='admin',
                email='admin@crm.com',
                created_at=datetime.utcnow()
            )
            db.session.add(admin_worker)
            db.session.commit()
            print("Admin worker created successfully.")
        except Exception as e:
            print("Error creating admin worker:", e)
    else:
        print("Admin worker already exists.")
