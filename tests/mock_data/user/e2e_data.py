"""
Mock data specifically for end-to-end user testing.
Contains UI-focused test scenarios and workflow data.
"""
from backend.src.enums.user_role import UserRole

"""
Mock data specifically for end-to-end user testing.
Contains UI-focused test scenarios and workflow data.
"""
from backend.src.enums.user_role import UserRole

# E2E User Workflow Test Data
E2E_USER_WORKFLOW = {
    "create": {
        "name": "E2E Test User",
        "email": "e2e.test@example.com",
        "role": UserRole.STAFF,
        "password": "E2ETest@123",
        "department_id": 1,
        "created_by_admin": True
    },
    "update": {
        "name": "Updated E2E User",
        "email": "updated.e2e@example.com", 
        "role": UserRole.MANAGER
    },
    "expected_responses": {
        "create_success": "successfully",
        "update_success": ["updated successfully", "users loaded successfully"],
        "delete_success": ["deleted successfully", "users loaded successfully"]
    }
}

# E2E Form Validation Test Data
E2E_FORM_VALIDATION = {
    "invalid_email": {
        "name": "Invalid Email User",
        "email": "not-an-email",
        "password": "Valid@123"
    },
    "weak_password": {
        "name": "Weak Password User", 
        "email": "weak@example.com",
        "password": "123"
    },
    "missing_name": {
        "name": "",
        "email": "missing.name@example.com",
        "password": "Valid@123"
    }
}

# E2E Navigation Test Data
E2E_NAVIGATION = {
    "pages": {
        "user_list": "user.html",
        "create_user": "create_user.html"
    },
    "buttons": {
        "create_new_user": "Create New User",
        "back_to_users": "← Back to Users",
        "refresh": "Refresh Users"
    }
}

# E2E Performance Test Data (for load testing scenarios)
E2E_BULK_USERS = [
    {
        "name": f"Bulk User {i}",
        "email": f"bulk.user.{i}@example.com",
        "role": UserRole.STAFF if i % 2 == 0 else UserRole.MANAGER,
        "password": f"BulkPass@{i}",
        "department_id": str((i % 3) + 1)
    }
    for i in range(1, 11)  # 10 test users for bulk operations
]

# E2E Role-Based Access Test Data
E2E_ROLE_SCENARIOS = {
    "staff_user": {
        "name": "Staff Member",
        "email": "staff@example.com",
        "role": UserRole.STAFF,
        "password": "Staff@123",
        "expected_permissions": ["view", "update_own"]
    },
    "manager_user": {
        "name": "Manager User",
        "email": "manager@example.com", 
        "role": UserRole.MANAGER,
        "password": "Manager@123",
        "expected_permissions": ["view", "update_own", "update_others", "delete"]
    },
    "director_user": {
        "name": "Director User",
        "email": "director@example.com",
        "role": UserRole.DIRECTOR, 
        "password": "Director@123",
        "expected_permissions": ["view", "update_any", "delete_any", "admin"]
    }
}

# E2E UI Element Selectors (for maintenance)
E2E_SELECTORS = {
    "forms": {
        "name_input": "name",
        "email_input": "email", 
        "password_input": "password",
        "role_select": "role",
        "department_input": "department_id",
        "admin_checkbox": "admin",
        "submit_button": "button[type='submit']"
    },
    "list_view": {
        "user_items": ".user-item",
        "user_info": ".user-info",
        "update_button": ".btn-update",
        "delete_button": ".btn-delete",
        "save_button": ".btn-save",
        "cancel_button": ".btn-cancel"
    },
    "status": {
        "status_element": "status",
        "refresh_button": "refresh"
    }
}

VALID_DEPARTMENT = {
    "department_id": 1,
    "department_name": "Engineering",
    "manager_id": 1
}

SEED_USER = {
    "user_id": 1,
    "email": "tester@example.com",
    "name": "Tester",
    "role": UserRole.STAFF.value,
    "admin": False,
    "hashed_pw": "hashed_pw",
    "department_id": None,
}