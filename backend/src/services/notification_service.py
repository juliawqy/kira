"""
Notification service for orchestrating different types of notifications
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from .email_service import get_email_service
from ..schemas.email import EmailResponse


logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications across different channels"""
    
    def __init__(self):
        self.email_service = get_email_service()
    
    def notify_task_updated(
        self,
        task_id: int,
        task_title: str,
        updated_by: str,
        updated_fields: List[str],
        assignee_email: str,
        assignee_name: Optional[str] = None,
        previous_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        task_url: Optional[str] = None
    ) -> EmailResponse:
        """
        Send notification when a task is updated
        
        Args:
            task_id: ID of the updated task
            task_title: Title of the task
            updated_by: Name/email of the person who updated the task
            updated_fields: List of field names that were updated
            assignee_email: Email of the task assignee
            assignee_name: Name of the task assignee
            previous_values: Previous values of updated fields
            new_values: New values of updated fields
            task_url: Direct URL to the task (optional)
        
        Returns:
            EmailResponse: Result of the email sending operation
        """
        try:
            logger.info(f"Sending task update notification for task {task_id} to {assignee_email}")
            
            # Send email notification
            email_response = self.email_service.send_task_update_notification(
                task_id=task_id,
                task_title=task_title,
                updated_by=updated_by,
                updated_fields=updated_fields,
                assignee_email=assignee_email,
                assignee_name=assignee_name,
                previous_values=previous_values,
                new_values=new_values,
                task_url=task_url
            )
            
            if email_response.success:
                logger.info(f"Task update notification sent successfully to {assignee_email}")
            else:
                logger.error(f"Failed to send task update notification: {email_response.message}")
            
            return email_response
            
        except Exception as e:
            logger.error(f"Error in notify_task_updated: {str(e)}")
            return EmailResponse(
                success=False,
                message=f"Notification service error: {str(e)}",
                recipients_count=0
            )
    
    def notify_multiple_users_task_updated(
        self,
        task_id: int,
        task_title: str,
        updated_by: str,
        updated_fields: List[str],
        recipients: List[Dict[str, str]],  # [{"email": "...", "name": "..."}]
        previous_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        task_url: Optional[str] = None
    ) -> List[EmailResponse]:
        """
        Send notification to multiple users when a task is updated
        
        Args:
            task_id: ID of the updated task
            task_title: Title of the task
            updated_by: Name/email of the person who updated the task
            updated_fields: List of field names that were updated
            recipients: List of recipients with email and name
            previous_values: Previous values of updated fields
            new_values: New values of updated fields
            task_url: Direct URL to the task (optional)
        
        Returns:
            List[EmailResponse]: Results of all email sending operations
        """
        responses = []
        
        for recipient in recipients:
            try:
                response = self.notify_task_updated(
                    task_id=task_id,
                    task_title=task_title,
                    updated_by=updated_by,
                    updated_fields=updated_fields,
                    assignee_email=recipient.get("email"),
                    assignee_name=recipient.get("name"),
                    previous_values=previous_values,
                    new_values=new_values,
                    task_url=task_url
                )
                responses.append(response)
            except Exception as e:
                logger.error(f"Failed to notify {recipient.get('email')}: {str(e)}")
                responses.append(EmailResponse(
                    success=False,
                    message=f"Failed to notify {recipient.get('email')}: {str(e)}",
                    recipients_count=0
                ))
        
        return responses


# Global notification service instance
notification_service = NotificationService()


def get_notification_service() -> NotificationService:
    """Get notification service instance"""
    return notification_service