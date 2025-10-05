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

