import time
from celery.utils.log import get_task_logger
from src.infrastructure.celery.celery_app import celery_app

logger = get_task_logger(__name__)

@celery_app.task
def send_email_task(email: str, subject: str):
    logger.info(f"STARTING: Sending email to {email} with subject {subject}")
    # Simulate heavy processing or I/O
    time.sleep(5)
    logger.info(f"COMPLETED: Email sent to {email}")
    return f"Email sent to {email}"

@celery_app.task
def periodic_health_check():
    logger.info("CRON: Performing system health check...")
    return "Health check passed"
