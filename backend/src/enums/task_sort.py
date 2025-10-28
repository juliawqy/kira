from enum import Enum

class TaskSort(str, Enum):

    PRIORITY_DESC = "priority_desc"
    PRIORITY_ASC = "priority_asc"   
    START_DATE_ASC = "start_date_asc"
    START_DATE_DESC = "start_date_desc"
    DEADLINE_ASC = "deadline_asc"
    DEADLINE_DESC = "deadline_desc"
    STATUS = "status"

ALLOWED_SORTS = {s.value for s in TaskSort}