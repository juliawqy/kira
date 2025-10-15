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

TASK_UPDATE_PAYLOAD = {
    "title": "Updated Task Title",
    "description": "Updated Task Description",
    "start_date": (date.today() + timedelta(days=2)),
    "deadline": (date.today() + timedelta(days=11)),
    "priority": 8,
    "project_id": 100,
}

EXPECTED_TASK_UPDATED = {
    "id": 1,
    "title": "Updated Task Title",
    "description": "Updated Task Description",
    "start_date": (date.today() + timedelta(days=2)),
    "deadline": (date.today() + timedelta(days=11)),
    "status": TaskStatus.TO_DO.value,
    "priority": 8,
    "project_id": 100,
    "active": True
}

TASK_UPDATE_PARTIAL_TITLE = {
    "title": "Only Title Updated"
}

TASK_UPDATE_PARTIAL_PRIORITY = {
    "priority": 7
}

TASK_UPDATE_PARTIAL_DATES = {
    "start_date": (date.today() + timedelta(days=2)),
    "deadline": (date.today() + timedelta(days=10))
}

TASK_UPDATE_EMPTY = {
    "title": None,
    "description": None,
    "start_date": None,
    "deadline": None,
    "priority": None,
    "project_id": None
}


VALID_PROJECT_ID = 123
VALID_PROJECT_ID_INACTIVE_TASK = 100

INVALID_STATUS = "INVALID_STATUS"
INVALID_TASK_ID_NONEXISTENT = 99999
EMPTY_PROJECT_ID = 99999
