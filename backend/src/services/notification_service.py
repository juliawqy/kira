"""
Notification service for orchestrating different types of notifications
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from .email_service import get_email_service
from ..schemas.email import EmailResponse


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class NotificationService:
    """Service for managing notifications across different channels"""
    
    def __init__(self):
        self.email_service = get_email_service()
    
    def notify_task_updated(
        self,
        task_id: int,
        task_title: str,
        updated_fields: List[str],
        previous_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        task_url: Optional[str] = None
    ) -> EmailResponse:
        
        try:
            logger.info(f"Processing task update notification for task {task_id}")
            
            # Send email notification to all relevant stakeholders
            email_response = self.email_service.send_task_update_notification(
                task_id=task_id,
                task_title=task_title,
                updated_fields=updated_fields,
                previous_values=previous_values,
                new_values=new_values,
                task_url=task_url
            )
            
            if email_response.success:
                logger.info(f"Task update notification sent successfully for task {task_id}")
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
    



# Global notification service instance
notification_service = NotificationService()


def get_notification_service() -> NotificationService:
    """Get notification service instance"""
    return notification_service