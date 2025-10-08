"""
Email-related Pydantic schemas for validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class EmailType(str, Enum):
    """Types of email notifications"""
    TASK_UPDATED = "task_updated"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_OVERDUE = "task_overdue"
    GENERAL_NOTIFICATION = "general_notification"


class EmailRecipient(BaseModel):
    """Email recipient information"""
    email: EmailStr
    name: Optional[str] = None


class EmailContent(BaseModel):
    """Email content structure"""
    subject: str = Field(..., min_length=1, max_length=200)
    html_body: Optional[str] = None
    text_body: Optional[str] = None
    template_name: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None


class EmailMessage(BaseModel):
    """Complete email message structure"""
    recipients: List[EmailRecipient] = Field(..., min_items=1)
    content: EmailContent
    email_type: EmailType = EmailType.GENERAL_NOTIFICATION
    cc: Optional[List[EmailRecipient]] = None
    bcc: Optional[List[EmailRecipient]] = None
    priority: Optional[str] = "normal"  # low, normal, high


class TaskUpdateEmailData(BaseModel):
    """Data structure for task update email notifications"""
    task_id: int
    task_title: str
    updated_by: str
    updated_fields: List[str]
    previous_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    task_url: Optional[str] = None
    assignee_email: EmailStr
    assignee_name: Optional[str] = None


class EmailResponse(BaseModel):
    """Response model for email operations"""
    success: bool
    message: str
    email_id: Optional[str] = None
    recipients_count: int = 0