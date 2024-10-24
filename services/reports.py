from backend import db
from backend.models import Analytics
from datetime import date
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_monthly_summary_report():
    """
    Generate a monthly summary report for analytics data.

    This function retrieves all analytics records for the current month and
    formats them into a list of dictionaries for further processing or reporting.

    Returns:
        list: A list of dictionaries containing analytics data, including
              the analytics ID, metric value, and the period start and end dates.

    Raises:
        ValueError: If no analytics data is found for the current month.
    """
    try:
        current_month = date.today().month
        logger.info(
            f"Generating monthly summary report for month: {current_month}")


        report = Analytics.query.filter(db.extract('month',
                                                   Analytics.period_start_date) == current_month).all()


        if not report:
            logger.warning(
                f"No analytics data found for month: {current_month}")
            raise ValueError(
                f"No analytics data found for the current month: {current_month}")


        formatted_report = [{
            'analytics_id': r.analytics_id,
            'metric_value': r.metric_value,
            'period_start': r.period_start_date,
            'period_end': r.period_end_date
        } for r in report]

        logger.info(
            f"Monthly summary report generated successfully with {len(formatted_report)} entries.")
        return formatted_report

    except Exception as e:
        logger.error(
            f"An error occurred while generating the monthly summary report: {str(e)}")
        raise e
