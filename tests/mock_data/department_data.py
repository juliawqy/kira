# tests/mock_data/department_data.py
from backend.src.enums.user_role import UserRole

VALID_ADD_DEPARTMENT = {
    "name": "Engineering",
    "manager": 1,
    "user_role": UserRole.HR, 
}

VALID_DEPARTMENT_1 = {
    "department_id": 1,
    "department_name": "Engineering",
    "manager_id": 1,
}

VALID_DEPARTMENT_2 = {
    "department_id": 2,
    "department_name": "Human Resources",
    "manager_id": 2,
}

INVALID_DEPARTMENT_NO_NAME = {
    "name": None,
    "manager": 3,
    "user_role": UserRole.HR,
}

INVALID_DEPARTMENT_NO_MANAGER = {
    "name": "Finance",
    "manager": None,
    "user_role": UserRole.HR,
}

INVALID_DEPARTMENT_NON_HR = {
    "name": "Engineering",
    "manager": 4,
    "user_role": UserRole.MANAGER, 
}

VALID_DEPARTMENT_ID = 1
INVALID_DEPARTMENT_ID = 999
