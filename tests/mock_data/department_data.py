# tests/mock_data/department_data.py
from backend.src.enums.user_role import UserRole

VALID_ADD_DEPARTMENT = {
    "department_name": "Human Resources",
    "manager_id": 2,
    "creator_id": 4,
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
    "department_name": None,
    "manager_id": 2,
    "creator_id": 4, 
}

INVALID_DEPARTMENT_NO_MANAGER = {
    "department_name": "Human Resources",
    "manager_id": None,
    "creator_id": 4, 
}

INVALID_DEPARTMENT_NON_HR = {
    "department_name": "Human Resources",
    "manager_id": 2,
    "creator_id": 1, 
}

INVALID_DEPARTMENT_NONEXISTENT_HR = {
    "department_name": "Human Resources",   
    "manager_id": 2,
    "creator_id": 9999,
}

VALID_DEPARTMENT_ID = 1
INVALID_DEPARTMENT_ID = 999
INVALID_USER_ID = 99999
