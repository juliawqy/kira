from backend.src.enums.user_role import UserRole

VALID_USER_ADMIN = {
    "user_id": 1,
    "name": "Alice Admin",
    "email": "alice.admin@example.com",
    "role": UserRole.MANAGER.value,
    "department_id": None,
    "admin": True,
    "password": "Adm!nPass123",
}

VALID_USER = {
    "user_id": 1,
    "name": "Bob Employee",
    "email": "bob.employee@example.com",
    "role": UserRole.STAFF.value,
    "department_id": None,
    "admin": False,
    "password": "Empl@yee123",
}

VALID_CREATE_PAYLOAD_ADMIN = {
    "name": "Alice Admin",
    "email": "alice.admin@example.com",
    "role": UserRole.MANAGER,
    "password": "Adm!nPass123",
    "department_id": None,
    "admin": True,
    "created_by_admin": True,  
}

VALID_CREATE_PAYLOAD_USER = {
    "name": "Bob Employee",
    "email": "bob.employee@example.com",
    "role": UserRole.STAFF,
    "password": "Empl@yee123",
    "department_id": None,
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
    "admin": "not_a_boolean",
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

INVALID_EMAIL_UPDATE = {
    "email": "alice.admin@example.com"  # assuming this email already exists
}

INVALID_INVALID_ROLE_UPDATE = {
    "role": "invalid_role"
}

VALID_UPDATE_NAME = {"name": "Alice A."}

VALID_PASSWORD_CHANGE = {
    "current_password": "Empl@yee123",
    "new_password": "NewP@ssword123"
}

INVALID_PASSWORD_CHANGE_WRONG_CURRENT = {
    "current_password": "WrongCurrent123",
    "new_password": "NewP@ssword123"
}

INVALID_USER_ID = 9999
