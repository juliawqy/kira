from enum import Enum

class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

ALLOWED_PRIORITIES = {p.value for p in TaskPriority}
