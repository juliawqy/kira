"""
Example integration showing how to add email notifications to task updates
This file demonstrates how to extend your existing task service with email notifications
"""
from typing import Optional, Dict, Any, List
from datetime import date

# Import your existing task service functions
from .task import update_task, update_task_status
from .notification_service import get_notification_service


class TaskNotificationService:
    """
    Service that wraps existing task operations and adds email notifications
    Use this instead of calling task functions directly when you want notifications
    """
    
    def __init__(self):
        self.notification_service = get_notification_service()
    
    def update_task_with_notification(
        self,
        task_id: int,
        updated_by: str,  # Name or email of person making the update
        assignee_email: str,  # Email of task assignee
        assignee_name: Optional[str] = None,
        # Task update parameters (same as your existing update_task function)
        title: Optional[str] = None,
        description: Optional[str] = None,
        start_date: Optional[date] = None,
        deadline: Optional[date] = None,
        priority: Optional[str] = None,
        collaborators: Optional[str] = None,
        notes: Optional[str] = None,
        parent_id: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Update a task and send email notification to assignee
        
        Returns:
            Dict with task update result and email notification result
        """
        
        # Get original task data for comparison
        from .task import get_task_by_id
        original_task = get_task_by_id(task_id)
        if not original_task:
            return {
                "task_updated": False,
                "email_sent": False,
                "error": f"Task {task_id} not found"
            }
        
        # Store original values for email comparison
        original_values = {
            "title": original_task.title,
            "description": original_task.description,
            "start_date": str(original_task.start_date) if original_task.start_date else None,
            "deadline": str(original_task.deadline) if original_task.deadline else None,
            "priority": original_task.priority,
            "collaborators": original_task.collaborators,
            "notes": original_task.notes,
            "parent_id": original_task.parent_id,
        }
        
        # Update the task using your existing function
        updated_task = update_task(
            task_id=task_id,
            title=title,
            description=description,
            start_date=start_date,
            deadline=deadline,
            priority=priority,
            collaborators=collaborators,
            notes=notes,
            parent_id=parent_id,
        )
        
        if not updated_task:
            return {
                "task_updated": False,
                "email_sent": False,
                "error": "Failed to update task"
            }
        
        # Determine what fields were updated
        updated_fields = []
        new_values = {}
        
        field_mappings = {
            "title": title,
            "description": description,
            "start_date": str(start_date) if start_date else None,
            "deadline": str(deadline) if deadline else None,
            "priority": priority,
            "collaborators": collaborators,
            "notes": notes,
            "parent_id": parent_id,
        }
        
        for field, new_value in field_mappings.items():
            if new_value is not None and str(new_value) != str(original_values[field]):
                updated_fields.append(field.replace("_", " ").title())
                new_values[field] = new_value
        
        # Send email notification if there were changes
        email_response = None
        if updated_fields:
            try:
                email_response = self.notification_service.notify_task_updated(
                    task_id=task_id,
                    task_title=updated_task.title,
                    updated_by=updated_by,
                    updated_fields=updated_fields,
                    assignee_email=assignee_email,
                    assignee_name=assignee_name,
                    previous_values=original_values,
                    new_values=new_values
                )
            except Exception as e:
                email_response = {"success": False, "message": str(e)}
        
        return {
            "task_updated": True,
            "task": {
                "id": updated_task.id,
                "title": updated_task.title,
                "status": updated_task.status,
            },
            "email_sent": email_response.success if email_response else False,
            "email_response": email_response.message if email_response else "No changes to notify",
            "updated_fields": updated_fields
        }
    
    def update_task_status_with_notification(
        self,
        task_id: int,
        new_status: str,
        updated_by: str,
        assignee_email: str,
        assignee_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update task status and send email notification
        """
        
        # Get original task for comparison
        from .task import get_task_by_id
        original_task = get_task_by_id(task_id)
        if not original_task:
            return {
                "task_updated": False,
                "email_sent": False,
                "error": f"Task {task_id} not found"
            }
        
        original_status = original_task.status
        
        # Update status using your existing function
        try:
            updated_task = update_task_status(task_id, new_status)
        except Exception as e:
            return {
                "task_updated": False,
                "email_sent": False,
                "error": str(e)
            }
        
        # Send email notification about status change
        email_response = None
        if original_status != new_status:
            try:
                email_response = self.notification_service.notify_task_updated(
                    task_id=task_id,
                    task_title=updated_task.title,
                    updated_by=updated_by,
                    updated_fields=["Status"],
                    assignee_email=assignee_email,
                    assignee_name=assignee_name,
                    previous_values={"status": original_status},
                    new_values={"status": new_status}
                )
            except Exception as e:
                email_response = {"success": False, "message": str(e)}
        
        return {
            "task_updated": True,
            "task": {
                "id": updated_task.id,
                "title": updated_task.title,
                "status": updated_task.status,
            },
            "email_sent": email_response.success if email_response else False,
            "email_response": email_response.message if email_response else "No status change",
            "status_changed": original_status != new_status
        }


# Global instance
task_notification_service = TaskNotificationService()


def get_task_notification_service() -> TaskNotificationService:
    """Get task notification service instance"""
    return task_notification_service