VALID_ADD = {
    "title": "Implement login",
    "description": "Add OAuth2 login to backend",
    "status": "Pending",
    "priority": "Medium",
    "start_date": "2025-09-01",
    "deadline": "2025-09-15",
    "collaborators": "Alice,Bob",
}

VALID_TASK_1 = {
    "id": 1,
    "title": "Implement login",
    "description": "Add OAuth2 login to backend",
    "status": "Pending",
    "priority": "Medium",
    "start_date": "2025-09-01",
    "deadline": "2025-09-15",
    "collaborators": "Alice,Bob",
}

VALID_TASK_2 = {
    "id": 2,
    "title": "Fix payments bug",
    "description": "Resolve critical issue in checkout",
    "status": "In-progress",
    "priority": "High",
    "start_date": "2025-09-10",
    "deadline": "2025-09-20",
    "collaborators": "Charlie",
}

INVALID_TASK_NO_TITLE = {
    "title": None,
    "description": "No title provided",
    "status": "Pending",
    "priority": "Medium",
    "start_date": "2025-09-01",
    "deadline": "2025-09-10",
    "collaborators": "Dave",
}

INVALID_TASK_NO_STATUS = {
    "title": "Task with no status",
    "description": "This should fail",
    "status": None,
    "priority": "High",
    "start_date": "2025-09-01",
    "deadline": "2025-09-10",
    "collaborators": "Eve",
}

INVALID_TASK_NO_PRIORITY = {
    "title": "Task with no priority",
    "description": "This should fail",
    "status": "Pending",
    "priority": None,
    "start_date": "2025-09-01",
    "deadline": "2025-09-10",
    "collaborators": "Frank",
}

INVALID_TASK_ID = 999 # ID does not exist in mock DB
