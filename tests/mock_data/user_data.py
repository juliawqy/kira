# DB-like records represented as plain dicts (no helper classes)
VALID_USER_ADMIN = {
    "user_id": 1,
    "name": "Alice Admin",
    "email": "alice.admin@example.com",
    "role": "admin",
    "department_id": 10,
    "admin": True,
    "password": "Adm!nPass123",
}

VALID_USER = {
    "user_id": 2,
    "name": "Bob Employee",
    "email": "bob.employee@example.com",
    "role": "employee",
    "department_id": 20,
    "admin": False,
    "password": "Empl@yee123",
}

# Create payloads (independent of above user dicts)
VALID_CREATE_PAYLOAD_ADMIN = {
    "name": "Alice Admin",
    "email": "alice.admin@example.com",
    "role": "admin",
    "password": "Adm!nPass123",
    "department_id": 10,
    "admin": True,
}

VALID_CREATE_PAYLOAD_USER = {
    "name": "Bob Employee",
    "email": "bob.employee@example.com",
    "role": "employee",
    "password": "Empl@yee123",
    "department_id": 20,
    "admin": False,
}

# Invalid create payloads
INVALID_CREATE_SHORT_PASSWORD = {
    "name": "Short Pass",
    "email": "short.pass@example.com",
    "role": "employee",
    "password": "short",
    "department_id": None,
    "admin": False,
}

INVALID_CREATE_NO_SPECIAL = {
    "name": "No Special",
    "email": "nospecial@example.com",
    "role": "employee",
    "password": "LongButNoSpecial1",
    "department_id": None,
    "admin": False,
}

INVALID_CREATE_BAD_EMAIL = {
    "name": "Bad Email",
    "email": "not-an-email",
    "role": "employee",
    "password": "Valid!Pass1",
    "department_id": None,
    "admin": False,
}

# Update payloads
VALID_UPDATE_NAME = {"name": "Alice A."}
VALID_UPDATE_EMAIL = {"email": "alice.a@example.com"}
VALID_UPDATE_ADMIN_TOGGLE = {"admin": False}

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

# Edge cases
LARGE_NAME = {"name": "A" * 1024}
LONG_EMAIL = {"email": "user+" + "a"*200 + "@example.com"}
INVALID_USER_ID = 9999
