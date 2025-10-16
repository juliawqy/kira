from backend.src.enums.user_role import UserRole

VALID_USER_ADMIN = {
    "user_id": 1,
    "name": "Alice Admin",
    "email": "alice.admin@example.com",
    "role": UserRole.MANAGER.value,
    "department_id": 10,
    "admin": True,
    "password": "Adm!nPass123",
}

VALID_USER = {
    "user_id": 2,
    "name": "Bob Employee",
    "email": "bob.employee@example.com",
    "role": UserRole.STAFF.value,
    "department_id": 20,
    "admin": False,
    "password": "Empl@yee123",
}

VALID_CREATE_PAYLOAD_ADMIN = {
    "name": "Alice Admin",
    "email": "alice.admin@example.com",
    "role": UserRole.MANAGER,
    "password": "Adm!nPass123",
    "department_id": 10,
    "admin": True,
    "created_by_admin": True,  
}

VALID_CREATE_PAYLOAD_USER = {
    "name": "Bob Employee",
    "email": "bob.employee@example.com",
    "role": UserRole.STAFF,
    "password": "Empl@yee123",
    "department_id": 20,
    "admin": False,
    "created_by_admin": True, 
}

# Invalid create payloads
INVALID_CREATE_SHORT_PASSWORD = {
    "name": "Short Pass",
    "email": "short.pass@example.com",
    "role": UserRole.STAFF,
    "password": "short",
    "department_id": None,
    "admin": False,
    "created_by_admin": True,
}

INVALID_CREATE_NO_SPECIAL = {
    "name": "No Special",
    "email": "nospecial@example.com",
    "role": UserRole.STAFF,
    "password": "LongButNoSpecial1",
    "department_id": None,
    "admin": False,
    "created_by_admin": True,
}

INVALID_CREATE_BAD_EMAIL = {
    "name": "Bad Email",
    "email": None,
    "role": UserRole.STAFF,
    "password": "Valid!Pass1",
    "department_id": None,
    "admin": False,
    "created_by_admin": True,
}

INVALID_CREATE_BAD_ROLE = {
    "name": "Bad Role",
    "email": "bad.role@example.com",
    "role": "not_a_valid_role",
    "password": "Valid!Pass1",
    "department_id": None,
    "admin": False,
    "created_by_admin": True,
}

INVALID_CREATE_NO_NAME = {
    "name": None,
    "email": "no.name@example.com",
    "role": UserRole.STAFF,
    "password": "Valid!Pass1",
    "department_id": None,
    "admin": False,
    "created_by_admin": True,
}

INVALID_CREATE_BAD_ADMIN = {
    "name": "Bad Admin",
    "email": "bad.admin@example.com",
    "role": UserRole.MANAGER,
    "password": "Adm!nPass123",
    "department_id": 10,
    "admin": "yes",
    "created_by_admin": True,
}

INVALID_CREATE_UNAUTHORISED = {
    "name": "Unauth User",
    "email": "unauth.user@example.com",
    "role": UserRole.STAFF,
    "password": "Unauth!Pass123",
    "department_id": 20,
    "admin": False,
    "created_by_admin": False,
}

# Update payloads
VALID_UPDATE_NAME = {"name": "Alice A."}
VALID_UPDATE_EMAIL = {"email": "alice.a@example.com"}
VALID_UPDATE_ADMIN_TOGGLE = {"admin": False}
VALID_UPDATE_DEPARTMENT = {"department_id": 30}

# Delete payloads
VALID_DELETE_PAYLOAD = {
    "user_id": 1,
    "is_admin": True
}

INVALID_DELETE_PAYLOAD_NONEXISTENT_USER = {
    "user_id": 9999,
    "is_admin": True
}

INVALID_DELETE_PAYLOAD_NOT_ADMIN = {
    "user_id": 1,
    "is_admin": False
}

# Password change payloads
VALID_PASSWORD_CHANGE = {
    "current_password": "Adm!nPass123",
    "new_password": "NewP@ssword123"
}
INVALID_PASSWORD_CHANGE_WEAK = {
    "current_password": "Adm!nPass123",
    "new_password": "weak"
}
INVALID_PASSWORD_CHANGE_WRONG_CURRENT = {
    "current_password": "wrongcurrent",
    "new_password": "Another!Pass1"
}
INVALID_PASSWORD_TYPE = 12345
INVALID_ADMIN_TYPE = "yes"
INVALID_EMAIL_DOESNT_EXIST = "notfound@example.com"

# Edge cases
LARGE_NAME = {"name": "A" * 1024}
LONG_EMAIL = {"email": "user+" + "a"*200 + "@example.com"}
INVALID_USER_ID = 9999
