# tests/mock_data/comment/integration_data.py
from datetime import datetime

# ------------------ VALID DATA ------------------

VALID_COMMENT_ID = 1
VALID_TASK_ID = 101
VALID_USER_ID = 11
VALID_PROJECT_ID = 5

VALID_COMMENT_TEXT = "This is a test comment"
UPDATED_COMMENT_TEXT = "This comment has been updated"

# ------------------ INVALID DATA ------------------

INVALID_COMMENT_ID = 9999
INVALID_TASK_ID = 99999
INVALID_USER_ID = 88888

# ------------------ USER SEED DATA ------------------

VALID_USER = {
    "user_id": VALID_USER_ID,
    "email": "tester@example.com",
    "name": "Tester",
    "role": "STAFF",
    "admin": False,
    "hashed_pw": "hashed_pw",
    "department_id": None,
}

ANOTHER_USER = {
    "user_id": 3,
    "email": "another@example.com",
    "name": "Another User",
    "role": "STAFF",
    "admin": False,
    "hashed_pw": "hashed_pw2",
    "department_id": None,
}

# ------------------ PROJECT SEED DATA ------------------

VALID_PROJECT = {
    "project_id": VALID_PROJECT_ID,
    "project_name": "Integration Test Project",
    "project_manager": VALID_USER_ID,
    "active": True,
}

# ------------------ TASK SEED DATA ------------------

VALID_TASK = {
    "id": VALID_TASK_ID,
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
    "comment": VALID_COMMENT_TEXT,
}

COMMENT_UPDATE_PAYLOAD = {
    "comment": UPDATED_COMMENT_TEXT,
}

COMMENT_MULTIPLE_USERS = [
    {"user_id": VALID_USER_ID, "comment": "User1 comment"},
    {"user_id": ANOTHER_USER["user_id"], "comment": "User2 comment"},
]

EXPECTED_COMMENT_FIELDS = [
    "comment_id",
    "task_id",
    "user_id",
    "comment",
    "timestamp",
]
COMMENT_LIST_TEXTS = ["First comment", "Second comment"]