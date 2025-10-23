from backend.src.enums.user_role import UserRole  

VALID_PROJECT_NAME = "AI Platform Upgrade"

VALID_PROJECT = {
    "project_id": 1,
    "project_name": "AI Platform Upgrade",
    "project_manager": 1,
    "active": True
}

MANAGER_USER = {
    "user_id": 1,
    "role": UserRole.MANAGER.value,
    "name": "Project Manager",
    "email": "user1@example.com",
    "hashed_pw": "hashed_dummy_password1",
    "admin": False,
    "department_id": None,
}

STAFF_USER = {
    "user_id": 2,
    "role": UserRole.STAFF.value,
    "name": "Project Staff",
    "email": "user2@example.com",
    "hashed_pw": "hashed_dummy_password2",
    "admin": False,
    "department_id": None
}

NOT_FOUND_ID = 9999

EMPTY_PROJECT_NAME = "   "  

TEST_PROJECT_ID = 1  

MISSING_ROLE_USER = {
    "user_id": 42,
    "role": None,
    "email": "user42@example.com",
    "hashed_pw": "hashed_dummy_password42"
}