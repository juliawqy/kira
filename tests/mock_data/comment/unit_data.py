# tests/mock_data/comment/unit_data.py
from datetime import datetime

# ------------------ COMMENT TEXT DATA ------------------
VALID_COMMENT_TEXT = "Initial comment text"
UPDATED_COMMENT_TEXT = "Updated comment text"
EMPTY_COMMENT_TEXT = "   "

# ------------------ IDS ------------------
VALID_COMMENT_ID = 1
ANOTHER_COMMENT_ID = 10
VALID_TASK_ID = 100
VALID_USER_ID = 200
INVALID_COMMENT_ID = 999
INVALID_TASK_ID = 9999

# ------------------ TIMESTAMP ------------------
DUMMY_TIMESTAMP = datetime(2025, 1, 1, 10, 0, 0)

# ------------------ MOCK OBJECTS ------------------
MOCK_COMMENT = {
    "comment_id": VALID_COMMENT_ID,
    "task_id": VALID_TASK_ID,
    "user_id": VALID_USER_ID,
    "comment": VALID_COMMENT_TEXT,
    "timestamp": DUMMY_TIMESTAMP,
}

MOCK_ANOTHER_COMMENT = {
    "comment_id": ANOTHER_COMMENT_ID,
    "task_id": VALID_TASK_ID,
    "user_id": VALID_USER_ID,
    "comment": VALID_COMMENT_TEXT,
    "timestamp": DUMMY_TIMESTAMP,
}

MOCK_UPDATED_COMMENT = {
    "comment_id": VALID_COMMENT_ID,
    "task_id": VALID_TASK_ID,
    "user_id": VALID_USER_ID,
    "comment": UPDATED_COMMENT_TEXT,
    "timestamp": DUMMY_TIMESTAMP,
}

MOCK_COMMENTS_LIST = [
    {"comment_id": 1, "comment": "A", "task_id": VALID_TASK_ID, "user_id": VALID_USER_ID},
    {"comment_id": 2, "comment": "B", "task_id": VALID_TASK_ID, "user_id": VALID_USER_ID},
]

MOCK_EMPTY_LIST = []

# ------------------ ERROR MESSAGES ------------------
ERR_COMMENT_NOT_FOUND = f"Comment ID {INVALID_COMMENT_ID} not found"
ERR_INVALID_TASK = f"Task ID {INVALID_TASK_ID} not found"
ERR_EMPTY_COMMENT = "Comment cannot be empty"
ERR_INVALID_TASK_ID = "Invalid task ID"
