from backend.src.enums.user_role import UserRole  

VALID_PROJECT_NAME = "AI Platform Upgrade"

MANAGER_USER = {
    "user_id": 1,
    "role": UserRole.MANAGER.value,
    "email": "user1@example.com"
}

STAFF_USER = {
    "user_id": 2,
    "role": UserRole.STAFF.value,
    "email": "user2@example.com"
}

NOT_FOUND_ID = 9999

# Additional users for assignment tests
ASSIGNABLE_USER = {
    "user_id": 3,
    "role": UserRole.STAFF.value,
    "email": "user3@example.com"
}

DUPLICATE_USER = {
    "user_id": 4,
    "role": UserRole.STAFF.value,
    "email": "user4@example.com"
}

EMPTY_PROJECT_NAME = "   "  

TEST_PROJECT_ID = 1  
