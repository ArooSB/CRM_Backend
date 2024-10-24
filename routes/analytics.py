from flask import Blueprint, jsonify, request, abort
from backend import db
from backend.models import Analytics
from flask_jwt_extended import jwt_required
from datetime import datetime

bp = Blueprint('analytics', __name__)


def validate_date(date_str):
    """
    Validates the date string and returns a datetime object.
    Raises a 400 error if the date format is invalid.
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        abort(400, description="Invalid date format. Use 'YYYY-MM-DD'.")


def validate_metric_value(value):
    """
    Validates if the provided metric value is valid.
    Acceptable values: 'active', 'deactivated', 'in-process'.
    """
    allowed_values = ['active', 'deactivated', 'in-process']
    if value.lower() not in allowed_values:
        abort(400,
              description=f"Invalid metric value. Must be one of {allowed_values}.")


def validate_required_fields(data, required_fields):
    """
    Ensures that the required fields are present in the provided data.
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        abort(400,
              description=f"Missing required fields: {', '.join(missing_fields)}")


@bp.route('/analytics/reports', methods=['GET'])
@jwt_required()
def get_monthly_report():
    """
    Generates a monthly report of analytics based on the provided date range.
    The report is grouped by customer_id, worker_id, and metric_value.
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Building SQL query for analytic report
    query = """
        SELECT customer_id, worker_id, metric_value, COUNT(*) as count
        FROM analytics
    """
    conditions = []

    if start_date:
        start_date = validate_date(start_date)
        conditions.append(
            f"period_start_date >= '{start_date.strftime('%Y-%m-%d')}'")

    if end_date:
        end_date = validate_date(end_date)
        conditions.append(
            f"period_end_date <= '{end_date.strftime('%Y-%m-%d')}'")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY customer_id, worker_id, metric_value"

    # Execute query and format results
    result = db.session.execute(query)
    report_data = [
        {
            'customer_id': row['customer_id'],
            'worker_id': row['worker_id'],
            'metric_value': row['metric_value'],
            'count': row['count']
        } for row in result
    ]

    return jsonify(report_data)


@bp.route('/analytics', methods=['POST'])
@jwt_required()
def create_analytics_entry():
    """
    Creates a new analytics entry.
    Expects JSON data with 'customer_id', 'worker_id', 'metric_value', 'period_start_date', and 'period_end_date'.
    """
    data = request.get_json()

    validate_required_fields(data, ['customer_id', 'worker_id', 'metric_value',
                                    'period_start_date', 'period_end_date'])
    validate_metric_value(data['metric_value'])

    period_start_date = validate_date(data['period_start_date'])
    period_end_date = validate_date(data['period_end_date'])

    new_analytics = Analytics(
        customer_id=data['customer_id'],
        worker_id=data['worker_id'],
        period_start_date=period_start_date,
        period_end_date=period_end_date,
        metric_value=data['metric_value'].lower()
    )

    db.session.add(new_analytics)
    db.session.commit()

    return jsonify({"message": "Analytics entry created successfully!",
                    "analytics_id": new_analytics.analytics_id}), 201


@bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """
    Retrieves analytics entries with optional filters like 'metric_value', 'customer_id', 'worker_id', and date range.
    Supports pagination.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    metric_value = request.args.get('metric_value')
    customer_id = request.args.get('customer_id')
    worker_id = request.args.get('worker_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Analytics.query

    if metric_value:
        validate_metric_value(metric_value)
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
        'analytics': [
            {
                'analytics_id': a.analytics_id,
                'customer_id': a.customer_id,
                'worker_id': a.worker_id,
                'metric_value': a.metric_value,
                'period_start': a.period_start_date.strftime('%Y-%m-%d'),
                'period_end': a.period_end_date.strftime('%Y-%m-%d'),
                'created_at': a.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': a.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            } for a in analytics.items
        ]
    }

    return jsonify(response)


@bp.route('/analytics/<int:id>', methods=['PUT'])
@jwt_required()
def update_analytics_entry(id):
    """
    Updates an existing analytics entry by its ID.
    Expects JSON data with fields like 'metric_value', 'period_start_date', and 'period_end_date'.
    """
    analytics = Analytics.query.get_or_404(id,
                                           description="Analytics entry not found!")

    data = request.get_json()
    validate_metric_value(data.get('metric_value', '').lower())

    analytics.period_start_date = validate_date(data['period_start_date'])
    analytics.period_end_date = validate_date(data['period_end_date'])
    analytics.metric_value = data['metric_value'].lower()
    analytics.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({"message": "Analytics entry updated successfully!"})


@bp.route('/analytics/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_analytics_entry(id):
    """
    Deletes an analytics entry by its ID.
    """
    analytics = Analytics.query.get_or_404(id,
                                           description="Analytics entry not found!")

    db.session.delete(analytics)
    db.session.commit()

    return jsonify({"message": "Analytics entry deleted successfully!"})
