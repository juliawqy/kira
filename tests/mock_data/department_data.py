# tests/mock_data/department_data.py

VALID_ADD_DEPARTMENT = {
    "name": "Engineering",
    "description": "Handles all product and infrastructure development.",
    "manager": "Alice Tan",
    "created_at": "2025-09-01",
}

VALID_DEPARTMENT_1 = {
    "id": 1,
    "name": "Engineering",
    "description": "Handles all product and infrastructure development.",
    "manager": "Alice Tan",
    "created_at": "2025-09-01",
}

VALID_DEPARTMENT_2 = {
    "id": 2,
    "name": "Human Resources",
    "description": "Manages hiring, onboarding, and employee welfare.",
    "manager": "Benjamin Lee",
    "created_at": "2025-08-20",
}

INVALID_DEPARTMENT_NO_NAME = {
    "name": None,
    "description": "Missing name should trigger validation error.",
    "manager": "Daphne Koh",
    "created_at": "2025-09-10",
}

INVALID_DEPARTMENT_NO_MANAGER = {
    "name": "Finance",
    "description": "Missing manager should trigger validation error.",
    "manager": None,
    "created_at": "2025-09-10",
}

VALID_DEPARTMENT_ID = 1
INVALID_DEPARTMENT_ID = 999  # Department ID that doesn't exist
