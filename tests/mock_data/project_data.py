from backend.src.enums.user_role import UserRole  

VALID_PROJECT_NAME = "AI Platform Upgrade"

MANAGER_USER = {
    "user_id": 1,
    "role": UserRole.MANAGER.value  
}

STAFF_USER = {
    "user_id": 2,
    "role": UserRole.STAFF.value  
}

NOT_FOUND_ID = 9999

# Additional users for assignment tests
ASSIGNABLE_USER = {
    "user_id": 3,
    "role": UserRole.STAFF.value
}

DUPLICATE_USER = {
    "user_id": 4,
    "role": UserRole.STAFF.value
}
EMPTY_PROJECT_NAME = "   "  

TEST_USER_EMAIL = "testuser@example.com"
TEST_PROJECT_ID = 1  
ASSIGNABLE_USER_EMAIL = "user3@example.com"
DUPLICATE_USER_EMAIL = "user4@example.com"
MANAGER_USER_EMAIL = "user1@example.com"