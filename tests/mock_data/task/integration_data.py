# tests/mock_data/task/integration_data.py
import json
from datetime import date, timedelta
from backend.src.enums.task_status import TaskStatus

TASK_CREATE_PAYLOAD = {
    "title": "Default Task",
    "start_date": (date.today() + timedelta(days=3)),
    "deadline": (date.today() + timedelta(days=10)),
    "project_id": 123
}

EXPECTED_TASK_RESPONSE = {
    "id": 1,
    "title": "Default Task",
    "description": None,
    "status": TaskStatus.TO_DO.value,
    "start_date": (date.today() + timedelta(days=3)),
    "deadline": (date.today() + timedelta(days=10)),
    "priority": 5,
    "project_id": 123,
    "active": True,
}

INVALID_TASK_CREATE = {
    "title": "Task with Invalid Create"
}

INVALID_TASK_CREATE_INVALID_PARENT = {
    "title": "Task with Invalid Parent",
    "parent_id": 99999,
    "project_id": 100
}

INVALID_TASK_CREATE_INACTIVE_PARENT = {
    "title": "Task with Inactive Parent",
    "parent_id": 1,
    "project_id": 100
}

TASK_2_PAYLOAD = {
    "title": "Task 2",
    "description": "Complete task with all fields",
    "start_date": date.today(),
    "deadline": (date.today() + timedelta(days=7)),
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 9,
    "project_id": 100,
    "active": True
}

TASK_2 = {
    "id": 2,
    "title": "Task 2",
    "description": "Complete task with all fields",
    "start_date": date.today(),
    "deadline": (date.today() + timedelta(days=7)),
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 9,
    "project_id": 100,
    "active": True
}

TASK_3_PAYLOAD = {
    "title": "Task 3",
    "start_date": (date.today() - timedelta(days=10)),
    "deadline": (date.today() - timedelta(days=5)),
    "project_id": 123,
    "priority": 1
}

TASK_3 = {
    "id": 3,
    "title": "Task 3",
    "description": None,
    "start_date": (date.today() - timedelta(days=10)),
    "deadline": (date.today() - timedelta(days=5)),
    "status": TaskStatus.TO_DO.value,
    "priority": 1,
    "project_id": 123,
    "active": True
}

TASK_4_PAYLOAD = {
    "title": "Task 4",
    "start_date": (date.today() - timedelta(days=10)),
    "deadline": (date.today() + timedelta(days=7)),
    "project_id": 123,
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 10
}

TASK_4 = {
    "id": 4,
    "title": "Task 4",
    "description": None,
    "start_date": (date.today() - timedelta(days=10)),
    "deadline": (date.today() + timedelta(days=7)),
    "status": TaskStatus.TO_DO.value,
    "priority": 10,
    "project_id": 123,
    "active": True
}

INACTIVE_TASK_PAYLOAD = {
    "title": "Inactive Task",
    "project_id": 100,
    "active": False
}

INACTIVE_TASK = {
    "id": 2,
    "title": "Inactive Task",
    "description": None,
    "status": TaskStatus.TO_DO.value,
    "start_date": None,
    "deadline": None,
    "priority": 5,
    "project_id": 100,
    "active": False,
}


INACTIVE_SUBTASK_PAYLOAD = {
    "title": "Inactive Subtask",
    "project_id": 123
}

INACTIVE_SUBTASK = {
    "id": 6,
    "title": "Inactive Subtask",
    "description": None,
    "status": TaskStatus.TO_DO.value,
    "start_date": None,
    "deadline": None,
    "priority": 5,
    "project_id": 123,
    "active": False,
}

TASK_CREATE_CHILD = {
    "title": "Task First Child",
    "project_id": 123,
}

EXPECTED_TASK_CHILD_RESPONSE = {
    "id": 2,
    "title": "Task First Child",
    "project_id": 123,
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "active": True,
    "description": None,
    "start_date": None,
    "deadline": None,
}

EXPECTED_RESPONSE_FIELDS = [
    "id", "title", "description", "start_date", "deadline", 
    "status", "priority", "project_id", "active"
]

SORT_PARAMETERS = [
    "priority_desc", "priority_asc", "start_date_asc", "start_date_desc", "deadline_asc","deadline_desc", "status"
]

INVALID_DATA_SORT = "invalid_sort"

FILTER_PARAMETERS = [
    json.dumps({"priority_range": [3, 7]}),
    json.dumps({"status": TaskStatus.TO_DO.value}),
    json.dumps({
        "deadline_range": [
            (date.today() - timedelta(days=5)).isoformat(),
            (date.today() + timedelta(days=8)).isoformat(),
        ]
    }),
    json.dumps({
        "start_date_range": [
            (date.today() - timedelta(days=10)).isoformat(),
            date.today().isoformat(),
        ]
    }),
]

MULTI_DATA_FILTER = json.dumps({
    "deadline_range": [
        (date.today() - timedelta(days=5)).isoformat(),
        (date.today() + timedelta(days=8)).isoformat(),
    ],
    "start_date_range": [
        (date.today() - timedelta(days=10)).isoformat(),
        date.today().isoformat(),
    ],
})

INVALID_DATA_FILTER = json.dumps({"invalid_filter": TaskStatus.TO_DO.value})

INVALID_DATA_FILTER_COMBI = [
    json.dumps({
        "start_date_range": [
            (date.today() - timedelta(days=10)).isoformat(),
            date.today().isoformat(),
        ],
        "status": TaskStatus.TO_DO.value
    }),
    json.dumps({
        "priority_range": [3, 7],
        "status": TaskStatus.TO_DO.value
    }),
]

FILTER_AND_SORT_QUERY =  "sort_by=status&filters=" + json.dumps({"priority_range": [3, 7]})








TASK_CREATE_EMPTY_TITLE = {
    "title": "",
    "project_id": 123
}

TASK_CREATE_PARENT = {
    "title": "Parent Task",
    "project_id": 100
}


TASK_CREATE_NONEXISTENT_PARENT = {
    "title": "Complete user authentication",
    "project_id": 100,
    "parent_id": 99999
}

TASK_CREATE_INACTIVE_PARENT_CHILD = {
    "title": "Performance optimization",
    "project_id": 100,
    "parent_id": None
}

TASK_CREATE_VALID_DATES = {
    "title": "Setup CI/CD pipeline",
    "project_id": 101,
    "start_date": (date.today() + timedelta(days=1)),
    "deadline": (date.today() + timedelta(days=7))
}

TASK_CREATE_INVALID_DATE = {
    "title": "Complete user authentication",
    "project_id": 100,
    "start_date": "invalid-date"
}

TASK_CREATE_STATUS_TODO = {
    "title": "Complete user authentication",
    "project_id": 100,
    "status": TaskStatus.TO_DO.value
}

TASK_CREATE_STATUS_IN_PROGRESS = {
    "title": "Database migration",
    "project_id": 100,
    "status": TaskStatus.IN_PROGRESS.value
}



ALL_VALID_STATUSES = [
    TaskStatus.TO_DO.value,
    TaskStatus.IN_PROGRESS.value,
    TaskStatus.COMPLETED.value,
    TaskStatus.BLOCKED.value
]



VALID_PROJECT_ID = 123
VALID_PROJECT_ID_INACTIVE_TASK = 100

INVALID_PRIORITIES = [-1, 0, 11, "High", None]
INVALID_PRIORITY_VALUES = [-1, 0, 11, 999]  
INVALID_PRIORITY_TYPES = ["High", 3.14, [], {}] 
INVALID_STATUSES = ["In progress", "DONE", "Todo", None, "", 123]
INVALID_TASK_ID_TYPE = ["123", 3.14, None]
INVALID_TASK_ID_NONEXISTENT = 99999
EMPTY_PROJECT_ID = 99999

EDGE_CASE_PRIORITY_BOUNDARY_LOW = {"priority": 1}
EDGE_CASE_PRIORITY_BOUNDARY_HIGH = {"priority": 10}

VALID_PARENT_TASK = {
    "id": 10,
    "title": "Parent Task",
    "description": "Main task with subtasks",
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 6,
    "project_id": 100,
    "active": True,
}

INACTIVE_PARENT_TASK = {
    "id": 11,
    "title": "Inactive Parent",
    "description": "Parent task that is archived",
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 7,
    "project_id": 100,
    "active": False,
}

INVALID_PARENT_IDS = [0, -1]

EXPECTED_TASK_MINIMAL_RESPONSE = {
    "id": 1,
    "title": "Default Task",
    "project_id": 123,
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "active": True,
    "description": None,
    "start_date": None,
    "deadline": None
}

EXPECTED_TASK_EXPLICIT_PRIORITY_RESPONSE = {
    "id": 1,
    "title": "Task with Explicit Priority",
    "description": None,
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 8,
    "project_id": 100,
    "active": True
}

EXPECTED_TASK_FULL_RESPONSE = {
    "id": 1,
    "title": "Full Task Details",
    "description": "Complete task with all fields",
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 9,
    "project_id": 123,
    "active": True,
    "start_date": date.today(),
    "deadline": (date.today() + timedelta(days=7))
}

EXPECTED_PARENT_TASK_RESPONSE = {
    "id": 1,
    "title": "Parent Task",
    "description": None,
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "project_id": 100,
    "active": True
}

EXPECTED_CHILD_TASK_RESPONSE = {
    "id": 2,
    "title": "Default Task",
    "project_id": 123,
    "description": None,
    "priority": 5,
    "status": TaskStatus.TO_DO.value,
    "active": True
}

EXPECTED_EMPTY_TITLE_RESPONSE = {
    "id": 1,
    "title": "",
    "description": None,
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "project_id": 123,
    "active": True
}

EXPECTED_VALID_DATES_RESPONSE = {
    "id": 1,
    "title": "Setup CI/CD pipeline",
    "description": None,
    "start_date": (date.today() + timedelta(days=1)),
    "deadline": (date.today() + timedelta(days=7)),
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "project_id": 101,
    "active": True
}

EXPECTED_TASK_TODO_RESPONSE = {
    "id": 1,
    "title": "Complete user authentication",
    "description": None,
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "project_id": 100,
    "active": True
}

EXPECTED_TASK_IN_PROGRESS_RESPONSE = {
    "id": 1,
    "title": "Database migration",
    "description": None,
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 5,
    "project_id": 100,
    "active": True
}

EXPECTED_TASK_COMPLETED_RESPONSE = {
    "id": 1,
    "title": "Setup CI/CD pipeline",
    "description": None,
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.COMPLETED.value,
    "priority": 5,
    "project_id": 101,
    "active": True
}

EXPECTED_TASK_BLOCKED_RESPONSE = {
    "id": 1,
    "title": "Performance optimization",
    "description": None,
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.BLOCKED.value,
    "priority": 5,
    "project_id": 102,
    "active": True
}

TASK_UPDATE_BASIC = {
    "title": "Updated Task Title",
    "description": "Updated description",
    "priority": 8,
    "start_date": (date.today() + timedelta(days=1)),
    "deadline": (date.today() + timedelta(days=14)),
}

TASK_UPDATE_PARTIAL_TITLE_ONLY = {
    "title": "Only Title Updated"
}

TASK_UPDATE_PARTIAL_PRIORITY = {
    "priority": 7
}

TASK_UPDATE_PARTIAL_DATES = {
    "start_date": (date.today() + timedelta(days=2)),
    "deadline": (date.today() + timedelta(days=10))
}

TASK_UPDATE_CLEAR_OPTIONAL_FIELDS = {
    "description": None,
    "start_date": None,
    "deadline": None
}

TASK_UPDATE_INVALID_PRIORITY_LOW = {
    "title": "Updated Task Title",
    "priority": 0
}

TASK_UPDATE_INVALID_PRIORITY_HIGH = {
    "title": "Updated Task Title", 
    "priority": 11
}

TASK_UPDATE_INVALID_PRIORITY_TYPE = {
    "title": "Updated Task Title",
    "priority": "High"
}

TASK_UPDATE_INVALID_DATE_FORMAT = {
    "title": "Updated Task Title",
    "start_date": "invalid-date-format"
}

TASK_UPDATE_EMPTY_TITLE = {
    "title": ""
}

TASK_UPDATE_INVALID_WITH_STATUS = {
    "title": "Updated Task Title",
    "description": "Updated description",
    "priority": 8,
    "status": TaskStatus.COMPLETED.value
}

TASK_UPDATE_INVALID_WITH_ACTIVE = {
    "title": "Updated Task Title",
    "description": "Updated description", 
    "priority": 8,
    "active": False
}

TASK_UPDATE_LONG_TEXT = {
    "title": "C" * 255,
    "description": "D" * 1000
}

TASK_UPDATE_PRIORITY_MIN = {
    "priority": 1
}

TASK_UPDATE_PRIORITY_MAX = {
    "priority": 10
}

STATUS_TRANSITION_TODO_TO_PROGRESS = {
    "initial_status": TaskStatus.TO_DO.value,
    "action": "start",
    "expected_status": TaskStatus.IN_PROGRESS.value
}

STATUS_TRANSITION_PROGRESS_TO_BLOCKED = {
    "initial_status": TaskStatus.IN_PROGRESS.value,
    "action": "block", 
    "expected_status": TaskStatus.BLOCKED.value
}

STATUS_TRANSITION_PROGRESS_TO_COMPLETED = {
    "initial_status": TaskStatus.IN_PROGRESS.value,
    "action": "complete",
    "expected_status": TaskStatus.COMPLETED.value
}

STATUS_TRANSITION_BLOCKED_TO_PROGRESS = {
    "initial_status": TaskStatus.BLOCKED.value,
    "action": "start",
    "expected_status": TaskStatus.IN_PROGRESS.value
}

STATUS_TRANSITION_BLOCKED_TO_COMPLETED = {
    "initial_status": TaskStatus.BLOCKED.value,
    "action": "complete",
    "expected_status": TaskStatus.COMPLETED.value
}

STATUS_TRANSITION_TODO_TO_COMPLETED = {
    "initial_status": TaskStatus.TO_DO.value,
    "action": "complete",
    "expected_status": TaskStatus.COMPLETED.value
}

STATUS_TRANSITION_TODO_TO_BLOCKED = {
    "initial_status": TaskStatus.TO_DO.value,
    "action": "block",
    "expected_status": TaskStatus.BLOCKED.value
}

DELETE_SOFT_BASIC_TASK = {
    "title": "Task to Soft Delete",
    "project_id": 123
}

DELETE_SOFT_TASK_WITH_CHILDREN = {
    "title": "Parent for Soft Delete Test",
    "project_id": 100
}

DELETE_SOFT_CHILD_TASK = {
    "title": "Child for Soft Delete Test", 
    "project_id": 100
}

DELETE_SOFT_WITH_DETACH_TRUE = {"detach_links": True}
DELETE_SOFT_WITH_DETACH_FALSE = {"detach_links": False}

DELETE_HARD_BASIC_TASK = {
    "title": "Task to Hard Delete",
    "project_id": 123
}

DELETE_HARD_TASK_WITH_FULL_DETAILS = {
    "title": "Full Task for Hard Deletion",
    "description": "Complete task with all fields for hard deletion test",
    "start_date": (date.today() + timedelta(days=1)),
    "deadline": (date.today() + timedelta(days=7)),
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 8,
    "project_id": 100,
    "active": True
}

DELETE_HARD_PARENT_TASK = {
    "title": "Parent Task for Hard Deletion",
    "description": "Parent task to test hard deletion behavior with children",
    "project_id": 100
}

DELETE_HARD_CHILD_TASK_TEMPLATE = {
    "title": "Child Task for Hard Deletion Test",
    "description": "Child task to test parent hard deletion behavior",
    "project_id": 100,
    "parent_id": None
}

DELETE_HARD_CHILD_TASK_1 = {
    "title": "First Child Task",
    "project_id": 100,
    "parent_id": None
}

DELETE_HARD_CHILD_TASK_2 = {
    "title": "Second Child Task", 
    "project_id": 100,
    "parent_id": None
}

DELETE_HARD_CHILD_TASK_3 = {
    "title": "Third Child Task",
    "project_id": 100,
    "parent_id": None
}

DELETE_HARD_SOFT_DELETED_TASK = {
    "title": "Soft Deleted Task for Hard Deletion",
    "description": "Task that will be soft deleted then hard deleted",
    "project_id": 101
}

DELETE_HARD_TODO_TASK = {
    "title": "TO_DO Task for Hard Deletion",
    "status": TaskStatus.TO_DO.value,
    "project_id": 102
}

DELETE_HARD_COMPLETED_TASK = {
    "title": "Completed Task for Hard Deletion",
    "status": TaskStatus.COMPLETED.value,
    "project_id": 102
}

DELETE_HARD_BLOCKED_TASK = {
    "title": "Blocked Task for Hard Deletion",
    "status": TaskStatus.BLOCKED.value,
    "project_id": 102
}