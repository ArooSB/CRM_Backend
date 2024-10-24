from backend.models import Worker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_notification(worker_id, message):
    """
    Sends a notification to a worker with a given message.

    Parameters:
        worker_id (int): The ID of the worker to send the notification to.
        message (str): The notification message to be sent.

    Raises:
        ValueError: If the worker ID is invalid or the worker is not found.
    """


    worker = Worker.query.get(worker_id)

    if not worker:
        logger.error(f"Worker with ID {worker_id} not found.")
        raise ValueError(f"Worker with ID {worker_id} not found.")


    notification_message = f"Notification to {worker.first_name} {worker.last_name} (ID: {worker.worker_id}): {message}"


    logger.info(notification_message)


    print(notification_message)
