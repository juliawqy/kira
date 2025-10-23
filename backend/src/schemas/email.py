from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from backend.src.enums.email import EmailType


class EmailRecipient(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class EmailContent(BaseModel):
    subject: str = Field(..., min_length=1, max_length=200)
    html_body: Optional[str] = None
    text_body: Optional[str] = None
    template_name: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None


class EmailMessage(BaseModel):
    recipients: List[EmailRecipient] = Field(..., min_items=1)
    content: EmailContent
    email_type: EmailType = EmailType.GENERAL_NOTIFICATION
    cc: Optional[List[EmailRecipient]] = None
    priority: Optional[int] = None 


class TaskUpdateEmailData(BaseModel):
    task_id: int
    task_title: str
    updated_by: str
    updated_fields: List[str]
    previous_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    assignee_email: EmailStr
    assignee_name: Optional[str] = None


class EmailResponse(BaseModel):
    success: bool
    message: str
    email_id: Optional[str] = None
    recipients_count: int = 0