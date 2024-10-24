from flask import Blueprint, request, jsonify
from backend import db
from backend.models import Worker
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps

bp = Blueprint('workers', __name__)

SECRET_KEY = 'aroo'


def role_required(role):
    """Decorator to restrict access based on worker role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(current_worker, *args, **kwargs):
            if current_worker.role != role:
                return jsonify({
                    "message": "You do not have permission to perform this action!"
                }), 403
            return f(current_worker, *args, **kwargs)
        return decorated_function
    return decorator


def token_required(f):
    """Decorator to require a valid JWT token for access."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing!"}), 403

        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_worker = Worker.query.get(data['worker_id'])
            if not current_worker:
                return jsonify({"message": "Worker not found!"}), 404
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 403

        return f(current_worker, *args, **kwargs)
    return decorated


@bp.route('/workers', methods=['POST'])
@token_required
@role_required('admin')
def create_worker(current_worker):
    """Create a new worker account. Only accessible by admin."""
    data = request.get_json()

    required_fields = ['username', 'password', 'first_name', 'last_name', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing fields!"}), 400

    if Worker.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists!"}), 400

    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_worker = Worker(
        username=data['username'],
        password_hash=hashed_password,
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=data['role']
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
    return jsonify([{
        'worker_id': w.worker_id,
        'username': w.username,
        'first_name': w.first_name,
        'last_name': w.last_name,
        'role': w.role
    } for w in workers])


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
        'worker_id': worker.worker_id,
        'is_admin': worker.role == 'admin'
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token, "message": "Worker logged in successfully!"})


@bp.route('/workers/<int:id>', methods=['PUT'])
@token_required
@role_required('admin')
def update_worker(current_worker, id):
    """Update an existing worker's information. Admin only."""
    worker = Worker.query.get(id)
    if not worker:
        return jsonify({"message": "Worker not found!"}), 404

    data = request.get_json()

    worker.first_name = data.get('first_name', worker.first_name)
    worker.last_name = data.get('last_name', worker.last_name)

    if current_worker.role == 'admin':
        worker.role = data.get('role', worker.role)

    db.session.commit()

    return jsonify({"message": "Worker updated successfully!"}), 201


@bp.route('/workers/password/<int:id>', methods=['PUT'])
@token_required
def update_worker_password(current_worker, id):
    """Update only the password for the worker."""
    if current_worker.worker_id != id and current_worker.role != 'admin':
        return jsonify({"message": "You can only update your own password!"}), 403

    worker = Worker.query.get(id)
    if not worker:
        return jsonify({"message": "Worker not found!"}), 404

    data = request.get_json()
    if 'password' not in data:
        return jsonify({"message": "Password is required!"}), 400

    hashed_password = generate_password_hash(data['password'], method='sha256')
    worker.password_hash = hashed_password
    db.session.commit()

    return jsonify({"message": "Password updated successfully!"}), 201


@bp.route('/workers/<int:id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_worker(current_worker, id):
    """Delete a worker's account."""
    worker = Worker.query.get(id)
    if not worker:
        return jsonify({"message": "Worker not found!"}), 404

    if current_worker.worker_id == worker.worker_id:
        return jsonify({"message": "You cannot delete your own account!"}), 403

    db.session.delete(worker)
    db.session.commit()

    return jsonify({"message": "Worker deleted successfully!"}), 201


@bp.route('/workers/me', methods=['GET'])
@token_required
def get_my_profile(current_worker):
    """Get the current worker's profile."""
    return jsonify({
        'worker_id': current_worker.worker_id,
        'username': current_worker.username,
        'first_name': current_worker.first_name,
        'last_name': current_worker.last_name,
        'role': current_worker.role
    })
