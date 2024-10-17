from flask import Blueprint, jsonify, request, abort
from backend import db
from backend.models import Analytics
from flask_jwt_extended import jwt_required
from datetime import datetime

bp = Blueprint('analytics', __name__)

def validate_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        abort(400, description="Invalid date format. Use 'YYYY-MM-DD'.")

@bp.route('/analytics/reports', methods=['GET'])
@jwt_required()
def get_monthly_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = """
        SELECT customer_id, worker_id, metric_value, COUNT(*) as count
        FROM analytics
    """

    conditions = []
    if start_date:
        start_date = validate_date(start_date)
        conditions.append(f"period_start_date >= '{start_date.strftime('%Y-%m-%d')}'")
    if end_date:
        end_date = validate_date(end_date)
        conditions.append(f"period_end_date <= '{end_date.strftime('%Y-%m-%d')}'")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY customer_id, worker_id, metric_value"

    result = db.session.execute(query)
    report_data = [{
        'customer_id': row['customer_id'],
        'worker_id': row['worker_id'],
        'metric_value': row['metric_value'],
        'count': row['count']
    } for row in result]

    return jsonify(report_data)

@bp.route('/analytics', methods=['POST'])
@jwt_required()
def create_analytics_entry():
    data = request.get_json()
    metric_value = data.get('metric_value', '').lower()

    if metric_value not in ['active', 'deactivated', 'in-process']:
        return jsonify({"message": "Invalid metric value. Must be 'active', 'deactivated', or 'in-process'."}), 400

    if not all(key in data for key in ['customer_id', 'worker_id', 'period_start_date', 'period_end_date']):
        return jsonify({"message": "Missing required fields!"}), 400

    period_start_date = validate_date(data['period_start_date'])
    period_end_date = validate_date(data['period_end_date'])

    new_analytics = Analytics(
        customer_id=data['customer_id'],
        worker_id=data['worker_id'],
        period_start_date=period_start_date,
        period_end_date=period_end_date,
        metric_value=metric_value
    )
    db.session.add(new_analytics)
    db.session.commit()

    return jsonify({"message": "Analytics entry created successfully!", "analytics_id": new_analytics.analytics_id}), 201

@bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    metric_value = request.args.get('metric_value')
    customer_id = request.args.get('customer_id')
    worker_id = request.args.get('worker_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Analytics.query

    if metric_value:
        query = query.filter_by(metric_value=metric_value.lower())
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    if worker_id:
        query = query.filter_by(worker_id=worker_id)
    if start_date:
        start_date = validate_date(start_date)
        query = query.filter(Analytics.period_start_date >= start_date)
    if end_date:
        end_date = validate_date(end_date)
        query = query.filter(Analytics.period_end_date <= end_date)

    analytics = query.paginate(page=page, per_page=per_page, error_out=False)

    response = {
        'total_entries': analytics.total,
        'page': analytics.page,
        'per_page': analytics.per_page,
        'analytics': [{
            'analytics_id': a.analytics_id,
            'customer_id': a.customer_id,
            'worker_id': a.worker_id,
            'metric_value': a.metric_value,
            'period_start': a.period_start_date.strftime('%Y-%m-%d'),
            'period_end': a.period_end_date.strftime('%Y-%m-%d'),
            'created_at': a.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': a.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        } for a in analytics.items]
    }

    return jsonify(response)

@bp.route('/analytics/<int:id>', methods=['PUT'])
@jwt_required()
def update_analytics_entry(id):
    analytics = Analytics.query.get(id)
    if not analytics:
        return jsonify({"message": "Analytics entry not found!"}), 404

    data = request.get_json()
    metric_value = data.get('metric_value', '').lower()

    if metric_value not in ['active', 'deactivated', 'in-process']:
        return jsonify({"message": "Invalid metric value. Must be 'active', 'deactivated', or 'in-process'."}), 400

    analytics.period_start_date = validate_date(data['period_start_date'])
    analytics.period_end_date = validate_date(data['period_end_date'])
    analytics.metric_value = metric_value
    analytics.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({"message": "Analytics entry updated successfully!"})

@bp.route('/analytics/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_analytics_entry(id):
    analytics = Analytics.query.get(id)
    if not analytics:
        return jsonify({"message": "Analytics entry not found!"}), 404

    db.session.delete(analytics)
    db.session.commit()

    return jsonify({"message": "Analytics entry deleted successfully!"})
