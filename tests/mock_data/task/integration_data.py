# tests/mock_data/task/integration_data.py
from datetime import date, timedelta
from backend.src.enums.task_status import TaskStatus

# ===============================================================================
# INT-001 Series: Task Creation Payloads (Based on unit_data patterns)
# ===============================================================================

TASK_CREATE_MINIMAL = {
    "title": "Default Task",
    "project_id": 123
}

TASK_CREATE_FULL = {
    "title": "Full Task Details",
    "description": "Complete task with all fields",
    "start_date": date.today().isoformat(),
    "deadline": (date.today() + timedelta(days=7)).isoformat(),
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 9,
    "project_id": 123,
    "active": True
}

# Priority validation payloads - using unit_data INVALID_PRIORITY_VALUES
TASK_CREATE_PRIORITY_TOO_LOW = {
    "title": "Task with Explicit Priority",
    "priority": 0,  # From INVALID_PRIORITY_VALUES
    "project_id": 100
}

TASK_CREATE_PRIORITY_TOO_HIGH = {
    "title": "Task with Explicit Priority", 
    "priority": 11,  # From INVALID_PRIORITY_VALUES
    "project_id": 100
}

TASK_CREATE_PRIORITY_MIN = {
    "title": "Task with Explicit Priority",
    "project_id": 100,
    "priority": 1  # From EDGE_CASE_PRIORITY_BOUNDARY_LOW
}

TASK_CREATE_PRIORITY_MAX = {
    "title": "Task with Explicit Priority",
    "project_id": 100,
    "priority": 10  # From EDGE_CASE_PRIORITY_BOUNDARY_HIGH
}

# Status validation payloads - using unit_data INVALID_STATUSES
TASK_CREATE_INVALID_STATUS = {
    "title": "Complete user authentication",
    "status": "In progress",  # From INVALID_STATUSES - wrong case
    "project_id": 100
}

# Required field validation payloads
TASK_CREATE_MISSING_TITLE = {
    "project_id": 123
}

TASK_CREATE_MISSING_PROJECT_ID = {
    "title": "Default Task"
}

TASK_CREATE_EMPTY_TITLE = {
    "title": "",
    "project_id": 123
}

# Parent-child relationship payloads - matching unit_data VALID_PARENT_TASK pattern
TASK_CREATE_PARENT = {
    "title": "Parent Task",
    "project_id": 100
}

TASK_CREATE_CHILD_TEMPLATE = {
    "title": "Database migration",
    "project_id": 100,
    "parent_id": None  # Will be set dynamically
}

TASK_CREATE_NONEXISTENT_PARENT = {
    "title": "Complete user authentication",
    "project_id": 100,
    "parent_id": 99999  # From INVALID_TASK_ID_NONEXISTENT
}

TASK_CREATE_INACTIVE_PARENT_CHILD = {
    "title": "Performance optimization",
    "project_id": 100,
    "parent_id": None  # Will be set dynamically
}

# Date validation payloads
TASK_CREATE_VALID_DATES = {
    "title": "Setup CI/CD pipeline",
    "project_id": 101,
    "start_date": (date.today() + timedelta(days=1)).isoformat(),
    "deadline": (date.today() + timedelta(days=7)).isoformat()
}

TASK_CREATE_INVALID_DATE = {
    "title": "Complete user authentication",
    "project_id": 100,
    "start_date": "invalid-date"
}

# All valid statuses - matching unit_data task patterns
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

TASK_CREATE_STATUS_COMPLETED = {
    "title": "Setup CI/CD pipeline",
    "project_id": 101,
    "status": TaskStatus.COMPLETED.value
}

TASK_CREATE_STATUS_BLOCKED = {
    "title": "Performance optimization",
    "project_id": 102,
    "status": TaskStatus.BLOCKED.value
}

# Null field handling
TASK_CREATE_NULL_FIELDS = {
    "title": "Default Task",
    "project_id": 123,
    "description": None,
    "start_date": None,
    "deadline": None
}

# Long text payloads
TASK_CREATE_LONG_TEXT = {
    "title": "A" * 255,  # Long title
    "description": "B" * 1000,  # Long description
    "project_id": 123
}

# Special characters
TASK_CREATE_SPECIAL_CHARS = {
    "title": "Task with émojis 🚀 & symbols ñoño @#$%",
    "description": "Description with 中文字符 and ñoño & special chars: <>\"'",
    "project_id": 123
}

# Multiple project payloads - using unit_data project_id values
TASK_CREATE_PROJECT_1 = {"title": "Default Task", "project_id": 123}
TASK_CREATE_PROJECT_2 = {"title": "Complete user authentication", "project_id": 100}
TASK_CREATE_PROJECT_3 = {"title": "Setup CI/CD pipeline", "project_id": 101}

# Response structure validation
TASK_CREATE_RESPONSE_TEST = {
    "title": "Task with Explicit Priority",
    "description": "Complete task with all fields",
    "project_id": 100,
    "priority": 8
}

# All valid statuses for testing - from unit_data TaskStatus usage
ALL_VALID_STATUSES = [
    TaskStatus.TO_DO.value,
    TaskStatus.IN_PROGRESS.value,
    TaskStatus.COMPLETED.value,
    TaskStatus.BLOCKED.value
]

# Expected response fields
EXPECTED_RESPONSE_FIELDS = [
    "id", "title", "description", "start_date", "deadline", 
    "status", "priority", "project_id", "active"
]

# ===============================================================================
# Additional constants from unit_data for consistency
# ===============================================================================

# Valid test values - matching unit_data
VALID_PROJECT_ID = 123
VALID_PROJECT_ID_INACTIVE_TASK = 100

# Invalid test data for parameterized tests - from unit_data
INVALID_PRIORITIES = [-1, 0, 11, "High", None]
INVALID_PRIORITY_VALUES = [-1, 0, 11, 999]  
INVALID_PRIORITY_TYPES = ["High", 3.14, [], {}] 
INVALID_STATUSES = ["In progress", "DONE", "Todo", None, "", 123]
INVALID_TASK_ID_TYPE = ["123", 3.14, None]
INVALID_TASK_ID_NONEXISTENT = 99999
EMPTY_PROJECT_ID = 99999

# Edge cases - from unit_data
EDGE_CASE_PRIORITY_BOUNDARY_LOW = {"priority": 1}  # Minimum valid
EDGE_CASE_PRIORITY_BOUNDARY_HIGH = {"priority": 10}  # Maximum valid

# Parent task data - matching unit_data patterns
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

# ===============================================================================
# INT-002 Series: Task Retrieval Payloads
# ===============================================================================

# Expected task responses for retrieval tests
EXPECTED_TASK_MINIMAL_RESPONSE = {
    "id" : 1,
    "title": "Default Task",
    "project_id": 123,
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "active": True,
    "description": None,
    "start_date": None,
    "deadline": None
}

EXPECTED_TASK_FULL_RESPONSE = {
    "id": 2,
    "title": "Full Task Details",
    "description": "Complete task with all fields",
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 9,
    "project_id": 123,
    "active": True,
    "start_date": date.today().isoformat(),
    "deadline": (date.today() + timedelta(days=7)).isoformat()
}

# Parent-child expected responses
EXPECTED_PARENT_TASK_RESPONSE = {
    "id": 3,
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
    "id": 4,
    "title": "Database migration",
    "description": None,
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "project_id": 100,
    "active": True
}

# Empty title expected response
EXPECTED_EMPTY_TITLE_RESPONSE = {
    "id": 5,
    "title": "",
    "description": None,
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "project_id": 123,
    "active": True
}

# Valid dates expected response
EXPECTED_VALID_DATES_RESPONSE = {
    "id": 6,
    "title": "Setup CI/CD pipeline",
    "description": None,
    "start_date": (date.today() + timedelta(days=1)).isoformat(),
    "deadline": (date.today() + timedelta(days=7)).isoformat(),
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "project_id": 101,
    "active": True
}

# Status-specific expected responses
EXPECTED_TASK_TODO_RESPONSE = {
    "id": 7,
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
    "id": 8,
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
    "id": 9,
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
    "id": 10,
    "title": "Performance optimization",
    "description": None,
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.BLOCKED.value,
    "priority": 5,
    "project_id": 102,
    "active": True
}

# ===============================================================================
# INT-003 Series: Task Update Payloads
# ===============================================================================

# Basic update payloads - matching unit_data patterns
TASK_UPDATE_BASIC = {
    "title": "Updated Task Title",
    "description": "Updated description",
    "priority": 8,
    "start_date": (date.today() + timedelta(days=1)).isoformat(),
    "deadline": (date.today() + timedelta(days=14)).isoformat(),
}

TASK_UPDATE_PARTIAL_TITLE_ONLY = {
    "title": "Only Title Updated"
}

TASK_UPDATE_PARTIAL_PRIORITY = {
    "priority": 7
}

TASK_UPDATE_PARTIAL_DATES = {
    "start_date": (date.today() + timedelta(days=2)).isoformat(),
    "deadline": (date.today() + timedelta(days=10)).isoformat()
}

TASK_UPDATE_CLEAR_OPTIONAL_FIELDS = {
    "description": None,
    "start_date": None,
    "deadline": None
}

# Invalid update payloads
TASK_UPDATE_INVALID_PRIORITY_LOW = {
    "title": "Updated Task Title",
    "priority": 0  # From INVALID_PRIORITY_VALUES
}

TASK_UPDATE_INVALID_PRIORITY_HIGH = {
    "title": "Updated Task Title", 
    "priority": 11  # From INVALID_PRIORITY_VALUES
}

TASK_UPDATE_INVALID_PRIORITY_TYPE = {
    "title": "Updated Task Title",
    "priority": "High"  # From INVALID_PRIORITY_TYPES
}

TASK_UPDATE_INVALID_DATE_FORMAT = {
    "title": "Updated Task Title",
    "start_date": "invalid-date-format"
}

TASK_UPDATE_EMPTY_TITLE = {
    "title": ""
}

# Status-related fields (should be rejected in PATCH)
TASK_UPDATE_INVALID_WITH_STATUS = {
    "title": "Updated Task Title",
    "description": "Updated description",
    "priority": 8,
    "status": TaskStatus.COMPLETED.value  # Should not be allowed in PATCH
}

TASK_UPDATE_INVALID_WITH_ACTIVE = {
    "title": "Updated Task Title",
    "description": "Updated description", 
    "priority": 8,
    "active": False  # Should not be allowed in PATCH
}

# Long text updates
TASK_UPDATE_LONG_TEXT = {
    "title": "C" * 255,
    "description": "D" * 1000
}

# Special characters updates
TASK_UPDATE_SPECIAL_CHARS = {
    "title": "Updated émojis 🔄 & symbols ñañá @#$%",
    "description": "Updated with 更新字符 and special chars: <>\"'"
}

# Boundary values for updates
TASK_UPDATE_PRIORITY_MIN = {
    "priority": 1
}

TASK_UPDATE_PRIORITY_MAX = {
    "priority": 10
}

# ===============================================================================
# INT-003 Status Update Payloads and Expected Responses
# ===============================================================================

# Status transition test scenarios
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

# Archive/Restore test scenarios -> Delete (soft delete) test scenarios
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

# Soft delete with detach options
DELETE_SOFT_WITH_DETACH_TRUE = {"detach_links": True}
DELETE_SOFT_WITH_DETACH_FALSE = {"detach_links": False}

# ===============================================================================
# INT-004 Series: Task Hard Deletion Payloads
# ===============================================================================

# Basic hard deletion test scenarios
DELETE_HARD_BASIC_TASK = {
    "title": "Task to Hard Delete",
    "project_id": 123
}

DELETE_HARD_TASK_WITH_FULL_DETAILS = {
    "title": "Full Task for Hard Deletion",
    "description": "Complete task with all fields for hard deletion test",
    "start_date": (date.today() + timedelta(days=1)).isoformat(),
    "deadline": (date.today() + timedelta(days=7)).isoformat(),
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 8,
    "project_id": 100,
    "active": True
}

# Parent task for hard deletion with children tests
DELETE_HARD_PARENT_TASK = {
    "title": "Parent Task for Hard Deletion",
    "description": "Parent task to test hard deletion behavior with children",
    "project_id": 100
}

DELETE_HARD_CHILD_TASK_TEMPLATE = {
    "title": "Child Task for Hard Deletion Test",
    "description": "Child task to test parent hard deletion behavior",
    "project_id": 100,
    "parent_id": None  # Will be set dynamically
}

# Multiple children scenario for hard deletion
DELETE_HARD_CHILD_TASK_1 = {
    "title": "First Child Task",
    "project_id": 100,
    "parent_id": None  # Will be set dynamically
}

DELETE_HARD_CHILD_TASK_2 = {
    "title": "Second Child Task", 
    "project_id": 100,
    "parent_id": None  # Will be set dynamically
}

DELETE_HARD_CHILD_TASK_3 = {
    "title": "Third Child Task",
    "project_id": 100,
    "parent_id": None  # Will be set dynamically
}

# Soft deleted task for hard deletion
DELETE_HARD_SOFT_DELETED_TASK = {
    "title": "Soft Deleted Task for Hard Deletion",
    "description": "Task that will be soft deleted then hard deleted",
    "project_id": 101
}

# Task with different statuses for hard deletion
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
