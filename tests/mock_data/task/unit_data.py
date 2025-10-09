from datetime import date, timedelta
from backend.src.enums.task_status import TaskStatus

VALID_DEFAULT_TASK = {
    "id": 1,
    "title": "Default Task",
    "description": None,
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "project_id": 123,
    "active": True,
}

VALID_TASK_EXPLICIT_PRIORITY = {
    "id": 2,
    "title": "Task with Explicit Priority",
    "description": None,
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 8,
    "project_id": 100,
    "active": True,
}

VALID_TASK_FULL = {
    "id": 3,
    "title": "Full Task Details",
    "description": "Complete task with all fields",
    "start_date": date.today(),
    "deadline": date.today() + timedelta(days=7),
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 9,
    "project_id": 123,
    "active": True,
}

INACTIVE_TASK = {
    "id": 4,
    "title": "Inactive Task",
    "description": "This task is inactive",
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "project_id": 100,
    "active": False,
}

VALID_TASK_TODO = {
    "id": 1,
    "title": "Complete user authentication",
    "description": "Implement login and registration system",
    "start_date": date.today() + timedelta(days=1),
    "deadline": date.today() + timedelta(days=7),
    "status": TaskStatus.TO_DO.value,
    "priority": 8,
    "project_id": 100,
    "active": True,
}

VALID_TASK_IN_PROGRESS = {
    "id": 2,
    "title": "Database migration",
    "description": "Migrate from SQLite to PostgreSQL",
    "start_date": date.today() - timedelta(days=2),
    "deadline": date.today() + timedelta(days=14),
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 9,
    "project_id": 100,
    "active": True,
}

VALID_TASK_COMPLETED = {
    "id": 3,
    "title": "Setup CI/CD pipeline",
    "description": "Configure GitHub Actions for automated testing",
    "start_date": date.today() - timedelta(days=10),
    "deadline": date.today() - timedelta(days=3),
    "status": TaskStatus.COMPLETED.value,
    "priority": 6,
    "project_id": 101,
    "active": True,
}

VALID_TASK_BLOCKED = {
    "id": 4,
    "title": "Performance optimization",
    "description": "Optimize database queries",
    "start_date": date.today() - timedelta(days=10),
    "deadline": date.today() + timedelta(days=14),
    "status": TaskStatus.BLOCKED.value,
    "priority": 5,
    "project_id": 102,
    "active": True,
}

VALID_CREATE_PAYLOAD_MINIMAL = {
    "title": "Default Task",
    "project_id": 100
}

VALID_CREATE_PAYLOAD_WITH_EXPLICIT_PRIORITY = {
    "title": "Task with Explicit Priority",
    "priority": 8,  # Different from default to test explicit priority
    "project_id": 100,
}

VALID_CREATE_PAYLOAD_FULL = {
    "title": "Full Task Details",
    "description": "Complete task with all fields",
    "start_date": date.today(),
    "deadline": date.today() + timedelta(days=7),
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 9,
    "project_id": 123,
    "active": True,
}

VALID_CREATE_PAYLOAD_WITH_PARENT = {
    "title": "Child Task",
    "priority": 4,
    "project_id": 100,
    "active": True,
    "parent_id": 1,
}

# Parent task for testing hierarchy
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

# Inactive parent task for testing validation
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

# Invalid create payloads
INVALID_CREATE_BAD_PRIORITY_LOW = {
    "title": "Bad Priority Low",
    "priority": 0,  # Invalid: below 1
    "project_id": 100,
}

INVALID_CREATE_BAD_PRIORITY_HIGH = {
    "title": "Bad Priority High",
    "priority": 11,  # Invalid: above 10
    "project_id": 100,
}

INVALID_CREATE_BAD_STATUS = {
    "title": "Bad Status",
    "status": "In progress",  # Invalid: wrong format (should be "In-progress")
    "priority": 5,
    "project_id": 100,
}

INVALID_CREATE_NONEXISTENT_PARENT = {
    "title": "Orphan Task",
    "priority": 5,
    "project_id": 100,
    "parent_id": 999999,  # Non-existent parent ID
}

INVALID_TASK_ID_NONEXISTENT = 99999
EMPTY_PROJECT_ID = 99999

# Update payloads
VALID_UPDATE_TITLE = {"title": "Updated Task Title"}
VALID_UPDATE_DESCRIPTION = {"description": "Updated description"}
VALID_UPDATE_PRIORITY = {"priority": 8}
VALID_PROJECT_ID = 123
VALID_PROJECT_ID_INACTIVE_TASK = 100
VALID_UPDATE_DATES = {
    "start_date": date.today() + timedelta(days=1),
    "deadline": date.today() + timedelta(days=14),
}

# Edge cases
EDGE_CASE_LONG_TITLE = {"title": "A" * 128}  # Max length
EDGE_CASE_LONG_DESCRIPTION = {"description": "B" * 256}  # Max length
EDGE_CASE_PRIORITY_BOUNDARY_LOW = {"priority": 1}  # Minimum valid
EDGE_CASE_PRIORITY_BOUNDARY_HIGH = {"priority": 10}  # Maximum valid

# Invalid test data for parameterized tests
INVALID_PRIORITIES = [-1, 0, 11, 999, "High", None]
INVALID_PRIORITY_VALUES = [-1, 0, 11, 999]  
INVALID_PRIORITY_TYPES = ["High", None, 3.14, [], {}] 
INVALID_STATUSES = ["In progress", "DONE", "Todo", None, "", 123]
INVALID_TASK_ID_TYPE = ["123", 3.14, None]
INVALID_PARENT_IDS = [0, -1]

# Mock task instances for testing relationships
MOCK_CHILD_TASKS = [
    {"id": 20, "title": "Child-1", "priority": 4},
    {"id": 21, "title": "Child-2", "priority": 7},
]

# Mock return values for session operations
MOCK_TASK_RETURN = {
    "id": 1,
    "title": "Mocked Task",
    "description": "Task created via mock",
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "project_id": 100,
    "active": True,
}
