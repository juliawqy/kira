from enum import Enum


class EmailType(str, Enum):
    TASK_UPDATED = "task_updated"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_OVERDUE = "task_overdue"
    UPCOMING_DEADLINE = "upcoming_deadline"
    OVERDUE_DEADLINE = "overdue_deadline"
    GENERAL_NOTIFICATION = "general_notification"
