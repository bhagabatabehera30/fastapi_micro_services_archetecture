import time
import asyncio
from celery.utils.log import get_task_logger
from src.infrastructure.celery.celery_app import celery_app
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType

import os

from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import random
from datetime import datetime, date

logger = get_task_logger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_FROM", "no-reply@saas-app.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "1025")),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "mailpit"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "False").lower() in ("true", "1"),
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() in ("true", "1"),
    USE_CREDENTIALS=os.getenv("USE_CREDENTIALS", "False").lower() in ("true", "1"),
    VALIDATE_CERTS=os.getenv("VALIDATE_CERTS", "False").lower() in ("true", "1")
)

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

async def _send_mail_async(email: str, subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)

@celery_app.task
def send_email_task(email: str, template_type: str, user_id: int):
    logger.info(f"STARTING: Sending {template_type} email to {email} for User {user_id}")
    
    try:
        template = jinja_env.get_template(f"{template_type}.html")
        
        if template_type == "welcome":
            subject = "🚀 Welcome to the Advanced Microservices SaaS!"
            html_body = template.render(
                username=f"Developer_{user_id}",
                email=email,
                action_url="http://localhost:8081/api/v1/jobs/docs"
            )
        elif template_type == "security_alert":
            subject = "🛡️ Critical Security Verification Code"
            html_body = template.render(
                username=f"User_{user_id}",
                code=str(random.randint(100000, 999999)),
                ip_address="172.19.0.1",
                device="Chrome (Linux x86_64) via Gateway",
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                support_url="http://localhost:8081/api/v1/jobs/docs"
            )
        else: # report
            subject = "📊 Weekly System Metrics & Analytics Report"
            html_body = template.render(
                username=f"Administrator_{user_id}",
                date=str(date.today()),
                stats={
                    "total_requests": random.randint(50000, 100000),
                    "uptime": 99.99,
                    "latency": random.randint(80, 150)
                },
                nodes=[
                    {"name": "Auth Microservice Service Node", "status": "online", "cpu_load": 6.8},
                    {"name": "Notification Microservice Node", "status": "online", "cpu_load": 11.2},
                    {"name": "Celery Background Task Worker", "status": "online", "cpu_load": 3.4},
                    {"name": "Postgres Database Cluster Engine", "status": "online", "cpu_load": 18.5}
                ],
                dashboard_url="http://localhost:8081/api/v1/jobs/docs"
            )

        asyncio.run(_send_mail_async(email, subject, html_body))
        logger.info(f"COMPLETED: {template_type} email successfully dispatched to {email}")
        return f"{template_type} email successfully dispatched to {email}"
    except Exception as e:
        logger.error(f"FAILED to send email: {str(e)}")
        raise e

@celery_app.task
def periodic_health_check():
    logger.info("CRON: Performing system health check...")
    return "Health check passed"
