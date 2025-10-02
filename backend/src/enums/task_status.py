from enum import Enum

class TaskStatus(str, Enum):
    TO_DO = "To-do"
    IN_PROGRESS = "In-progress"
    COMPLETED = "Completed"
    BLOCKED = "Blocked"

ALLOWED_STATUSES = {s.value for s in TaskStatus}
