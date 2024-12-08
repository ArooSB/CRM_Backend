from flask import Blueprint, jsonify, request
from backend import db
from backend.models  import SalesLead
from datetime import datetime


bp = Blueprint('revenue', __name__)

@bp.route('/revenue', methods=['GET'])
def calculate_revenue():
    """
    Calculate total revenue based on sales leads.
    Optionally filter by a date range using 'start_date' and 'end_date'.
    """
    try:
        start_date = request.args.get('start_date')  # Format: YYYY-MM-DD
        end_date = request.args.get('end_date')      # Format: YYYY-MM-DD

        query = db.session.query(SalesLead)

        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(SalesLead.created_at >= start_date)
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(SalesLead.created_at <= end_date)

        total_revenue = sum(lead.potential_value or 0 for lead in query.all())

        return jsonify({'success': True, 'total_revenue': total_revenue}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
