from flask import Blueprint, jsonify, request
from backend.models import WorkerCalendar, Worker
from backend import db

# Initialize the Blueprint with name 'bp'
bp = Blueprint('calendar', __name__)

@bp.route('/calendar', methods=['GET'])
def get_worker_calendar():
    """
    Retrieve all calendar events for all workers.
    """
    try:
        events = WorkerCalendar.query.all()

        calendar_data = []
        for event in events:
            calendar_data.append({
                'worker_id': event.worker_id,
                'worker_name': event.worker.name if event.worker else "Unknown",
                'event_title': event.event_title,
                'event_date': event.event_date.strftime('%Y-%m-%d'),
                'event_time': event.event_time.strftime('%H:%M:%S') if event.event_time else None,
                'description': event.description
            })

        return jsonify({
            'success': True,
            'calendar_events': calendar_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
