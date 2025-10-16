from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from backend.src.services.email_service import get_email_service
from backend.src.schemas.email import EmailMessage, EmailRecipient, EmailType
from backend.src.config.email_config import get_email_settings


router = APIRouter(prefix="/notification", tags=["notification"])


class TaskUpdateNotifyRequest(BaseModel):
    task_id: int = Field(..., description="Task identifier")
    task_title: str = Field(..., description="Task title to use in the email subject")
    updated_fields: List[str] = Field(default_factory=list)
    previous_values: Dict[str, Any] = Field(default_factory=dict)
    new_values: Dict[str, Any] = Field(default_factory=dict)
    task_url: Optional[str] = None
    recipient_email: Optional[str] = Field(None, description="Override recipient email; falls back to TEST_RECIPIENT_EMAIL if unset")
    recipient_name: Optional[str] = None


@router.post("/task-update-notify")
def task_update_notify(payload: TaskUpdateNotifyRequest):
    settings = get_email_settings()
    email_service = get_email_service()

    # Determine recipient: explicit from request, else TEST_RECIPIENT_EMAIL, else sender (last resort)
    recipient_email = (
        payload.recipient_email
        or getattr(settings, "test_recipient_email", None)
        or settings.fastmail_from_email
    )
    recipient_name = payload.recipient_name or getattr(settings, "test_recipient_name", None) or "Task Subscriber"

    recipients = [EmailRecipient(email=recipient_email, name=recipient_name)]

    template_data = {
        "task_id": payload.task_id,
        "task_title": payload.task_title,
        "updated_by": "In-App Demo",
        "updated_fields": payload.updated_fields,
        "previous_values": payload.previous_values or {},
        "new_values": payload.new_values or {},
        "task_url": payload.task_url or f"{settings.app_url}/tasks/{payload.task_id}",
    }

    message = EmailMessage(
        recipients=recipients,
        content={
            "subject": f"Task Updated: {payload.task_title}",
            "template_name": "task_updated",
            "template_data": template_data,
        },
        email_type=EmailType.TASK_UPDATED,
    )

    response = email_service.send_email(message)
    return {
        "success": response.success,
        "message": response.message,
        "recipients_count": response.recipients_count,
        "to": [r.email for r in recipients],
    }
