from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from backend.src.services.email_service import get_email_service
from backend.src.schemas.email import EmailMessage, EmailRecipient, EmailType
from backend.src.config.email_config import get_email_settings
from backend.src.services.notification_service import get_notification_service
import logging
from backend.src.schemas.email import EmailResponse


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
    # Use the actual global EmailService instance so settings overrides are effective
    email_service = get_email_service()
    settings = email_service.settings
    notification_service = get_notification_service()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Determine recipient: explicit from request, else TEST_RECIPIENT_EMAIL, else sender (last resort)
    # Optionally override the test recipient for this request to emulate actual notification flow
    restore_recipient = getattr(settings, "test_recipient_email", None)
    # Log what client asked for
    logger.info(
        "[NotificationAPI] Requested recipient override | payload_recipient=%s",
        payload.recipient_email,
    )
    # For this demo endpoint, always honor payload override when provided
    if payload.recipient_email:
        settings.test_recipient_email = payload.recipient_email
        settings.test_recipient_name = payload.recipient_name or getattr(settings, "test_recipient_name", None)

    # Log the effective recipient that will be used by EmailService
    effective_to = getattr(settings, "test_recipient_email", None) or settings.fastmail_from_email
    logger.info(
        "[NotificationAPI] Effective recipient | to=%s (override=%s restore_prev=%s)",
        effective_to,
        bool(payload.recipient_email),
        bool(restore_recipient),
    )

    try:
        email_response: EmailResponse = notification_service.notify_task_updated(
            task_id=payload.task_id,
            task_title=payload.task_title,
            updated_fields=payload.updated_fields,
            previous_values=payload.previous_values,
            new_values=payload.new_values,
            task_url=payload.task_url,
        )
    finally:
        # Restore previous test recipient to avoid leaking overrides
        settings.test_recipient_email = restore_recipient

    if email_response.success:
        logger.info("[NotificationAPI] Notification sent via service | task_id=%s", payload.task_id)
    else:
        logger.error("[NotificationAPI] Notification failed | reason=%s", email_response.message)
    return {
        "success": email_response.success,
        "message": email_response.message,
        "recipients_count": email_response.recipients_count,
    }
