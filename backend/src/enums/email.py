from enum import Enum


class EmailType(str, Enum):
    TASK_UPDATED = "task_updated"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_OVERDUE = "task_overdue"
    GENERAL_NOTIFICATION = "general_notification"
