# tests/mock_data/comment/integration_data.py
from datetime import datetime
from backend.src.enums.user_role import UserRole

# ------------------ VALID DATA ------------------

VALID_COMMENT_ID = 1
VALID_TASK_ID = 1
VALID_USER_ID = 1
VALID_PROJECT_ID = 1

# ------------------ INVALID DATA ------------------

INVALID_COMMENT_ID = 9999
INVALID_TASK_ID = 99999
INVALID_USER_ID = 88888

# ------------------ SEED DATA ------------------

VALID_USER = {
    "user_id": 1,
    "email": "tester@example.com",
    "name": "Tester",
    "role": UserRole.STAFF.value,
    "admin": False,
    "hashed_pw": "hashed_pw",
    "department_id": None,
}

ANOTHER_USER = {
    "user_id": 2,
    "email": "another@example.com",
    "name": "Another User",
    "role": UserRole.STAFF.value,
    "admin": False,
    "hashed_pw": "hashed_pw2",
    "department_id": None,
}

VALID_PROJECT = {
    "project_id": 1,
    "project_name": "Integration Test Project",
    "project_manager": 1,
    "active": True,
}

VALID_TASK = {
    "id": 1,
    "title": "Task for comments",
    "description": "Integration test task",
    "status": "To-do",
    "priority": 5,
    "project_id": VALID_PROJECT_ID,
    "active": True,
}

# ------------------ COMMENT PAYLOADS ------------------

COMMENT_CREATE_PAYLOAD = {
    "user_id": VALID_USER_ID,
    "comment": "This is a test comment",
}

INVALID_CREATE_NONEXISTENT_USER = {
    "user_id": INVALID_USER_ID,
    "comment": "This is a test comment",
}

COMMENT_RESPONSE = {
    "comment_id": VALID_COMMENT_ID,
    "task_id": VALID_TASK_ID,
    "user_id": VALID_USER_ID,
    "comment": "This is a test comment",
    "timestamp": datetime.now().isoformat(),
}

COMMENT_UPDATE_PAYLOAD = {
    "comment": "This comment has been updated",
    "requesting_user_id": VALID_USER_ID,
}

COMMENT_UPDATED_RESPONSE = {
    "comment_id": VALID_COMMENT_ID,
    "task_id": VALID_TASK_ID,
    "user_id": VALID_USER_ID,
    "comment": "This comment has been updated",
    "timestamp": datetime.now().isoformat(),
}

COMMENT_MULTIPLE_USERS = [
    {"user_id": VALID_USER_ID, "comment": "User1 comment"},
    {"user_id": ANOTHER_USER["user_id"], "comment": "User2 comment"},
]

COMMENT_MULTIPLE_RESPONSE = [
    {"comment_id": 1, "task_id": VALID_TASK_ID, "user_id": VALID_USER_ID, "comment": "User1 comment", "timestamp": datetime.now().isoformat()},
    {"comment_id": 2, "task_id": VALID_TASK_ID, "user_id": ANOTHER_USER["user_id"], "comment": "User2 comment", "timestamp": datetime.now().isoformat()},
]

EXPECTED_COMMENT_FIELDS = [
    "comment_id",
    "task_id",
    "user_id",
    "comment",
    "timestamp",
]
COMMENT_LIST_TEXTS = ["First comment", "Second comment"]