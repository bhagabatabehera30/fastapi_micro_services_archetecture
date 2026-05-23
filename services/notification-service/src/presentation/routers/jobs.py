from fastapi import APIRouter, Depends, HTTPException
from src.infrastructure.celery.tasks import send_email_task
from packages.shared.auth.middleware import get_current_user_id

router = APIRouter()

@router.post("/trigger-email")
def trigger_email(email: str, current_user_id: int = Depends(get_current_user_id)):
    """
    Triggers an email sending background job. 
    Requires authentication via JWT (passed in Authorization header).
    """
    task = send_email_task.delay(email, f"Welcome to Advanced Microservices, User {current_user_id}!")
    return {"task_id": task.id, "status": "Queued", "user_id": current_user_id}
