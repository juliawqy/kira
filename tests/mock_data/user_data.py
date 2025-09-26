# DB-like records represented as plain dicts (no helper classes)
VALID_USER_ADMIN = {
    "user_id": 1,
    "name": "Alice Admin",
    "email": "alice.admin@example.com",
    "role": "admin",
    "department_id": 10,
    "admin": True,
    # plain-text password for input payloads; tests will mock hashing/verification
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

# Create payloads (what you'd send to create_user)
VALID_CREATE_PAYLOAD_ADMIN = {
    "name": VALID_USER_ADMIN["name"],
    "email": VALID_USER_ADMIN["email"],
    "role": VALID_USER_ADMIN["role"],
    "password": VALID_USER_ADMIN["password"],
    "department_id": VALID_USER_ADMIN["department_id"],
    "admin": True,
}

VALID_CREATE_PAYLOAD_USER = {
    "name": VALID_USER["name"],
    "email": VALID_USER["email"],
    "role": VALID_USER["role"],
    "password": VALID_USER["password"],
    "department_id": VALID_USER["department_id"],
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
}

# Update payloads
VALID_UPDATE_NAME = {"name": "Alice A."}
VALID_UPDATE_EMAIL = {"email": "alice.a@example.com"}
VALID_UPDATE_ADMIN_TOGGLE = {"admin": False}

# Password change payloads
VALID_PASSWORD_CHANGE = {
    "current_password": VALID_USER_ADMIN["password"],
    "new_password": "NewP@ssword123"
}
INVALID_PASSWORD_CHANGE_WEAK = {
    "current_password": VALID_USER_ADMIN["password"],
    "new_password": "weak"
}
INVALID_PASSWORD_CHANGE_WRONG_CURRENT = {
    "current_password": "wrongcurrent",
    "new_password": "Another!Pass1"
}

# Edge cases
LARGE_NAME = {"name": "A" * 1024}
LONG_EMAIL = {"email": "user+" + "a"*200 + "@example.com"}
