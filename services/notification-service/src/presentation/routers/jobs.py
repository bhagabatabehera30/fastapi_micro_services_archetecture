from fastapi import APIRouter, Depends, HTTPException
from src.infrastructure.celery.tasks import send_email_task
from packages.shared.auth.middleware import get_current_user_id

from typing import Literal

router = APIRouter()

@router.post("/trigger-email")
def trigger_email(
    email: str,
    template_type: Literal["welcome", "security_alert", "report"] = "welcome",
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Triggers a rich HTML email background job using the specified template.
    Requires authentication via JWT (passed in Authorization header).
    """
    task = send_email_task.delay(email, template_type, current_user_id)
    return {"task_id": task.id, "status": "Queued", "template_type": template_type, "user_id": current_user_id}
