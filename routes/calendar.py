from flask import Blueprint, jsonify, request
from backend import db
from backend.models import WorkerCalendar
from datetime import datetime

bp = Blueprint('calendar', __name__)

# Route to view all calendar events for workers
@bp.route('/calendar', methods=['GET'])
def get_calendar_events():
    """
    Get all calendar events for workers.
    Optionally, filter by worker ID and date range.
    """
    try:
        worker_id = request.args.get('worker_id', type=int)  # Optional worker filter
        start_date = request.args.get('start_date')  # Format: YYYY-MM-DD
        end_date = request.args.get('end_date')      # Format: YYYY-MM-DD

        query = db.session.query(WorkerCalendar)

        # Apply filter by worker ID if provided
        if worker_id:
            query = query.filter(WorkerCalendar.worker_id == worker_id)

        # Apply filters by date range if provided
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(WorkerCalendar.event_date >= start_date)
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(WorkerCalendar.event_date <= end_date)

        events = query.all()

        # Format the result to return it as a list of dictionaries
        calendar_events = [
            {
                'event_title': event.event_title,
                'event_date': event.event_date.strftime('%Y-%m-%d'),
                'event_time': event.event_time.strftime('%H:%M') if event.event_time else None,
                'description': event.description,
                'worker_id': event.worker_id
            }
            for event in events
        ]

        return jsonify({
            'success': True,
            'calendar_events': calendar_events
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
