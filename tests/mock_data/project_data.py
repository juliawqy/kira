from backend.src.enums.user_role import UserRole  

VALID_PROJECT_NAME = "AI Platform Upgrade"

MANAGER_USER = {
    "user_id": 1,
    "role": UserRole.MANAGER.value,
    "email": "user1@example.com",
    "hashed_pw": "hashed_dummy_password1"
}

STAFF_USER = {
    "user_id": 2,
    "role": UserRole.STAFF.value,
    "email": "user2@example.com",
    "hashed_pw": "hashed_dummy_password2"
}

NOT_FOUND_ID = 9999

# Additional users for assignment tests
ASSIGNABLE_USER = {
    "user_id": 3,
    "role": UserRole.STAFF.value,
    "email": "user3@example.com",
    "hashed_pw": "hashed_dummy_password3"
}

DUPLICATE_USER = {
    "user_id": 4,
    "role": UserRole.STAFF.value,
    "email": "user4@example.com",
    "hashed_pw": "hashed_dummy_password4"
}

EMPTY_PROJECT_NAME = "   "  

TEST_PROJECT_ID = 1  

MISSING_ROLE_USER = {
    "user_id": 42,
    "role": None,
    "email": "user42@example.com",
    "hashed_pw": "hashed_dummy_password42"
}