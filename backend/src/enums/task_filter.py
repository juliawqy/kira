from enum import Enum

class TaskFilter(str, Enum):
    PRIORITY_RANGE = "priority_range"
    STATUS = "status"
    DEADLINE_RANGE = "deadline_range"
    START_DATE_RANGE = "start_date_range"

ALLOWED_FILTERS = {f.value for f in TaskFilter}