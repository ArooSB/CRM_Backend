from backend import db
from backend.models import Analytics
from datetime import date

def generate_monthly_summary_report():
    current_month = date.today().month
    report = Analytics.query.filter(db.extract('month', Analytics.period_start_date) == current_month).all()

    return [{
        'analytics_id': r.analytics_id,
        'metric_value': r.metric_value,
        'period_start': r.period_start_date,
        'period_end': r.period_end_date
    } for r in report]


