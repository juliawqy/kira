from backend.src.enums.user_role import UserRole

USER_ADMIN = {
    "name": "Alice Admin",
    "email": "alice.admin@example.com",
    "role": UserRole.MANAGER.value,
    "hashed_pw": "Adm!nPass123",
    "department_id": 10,
    "admin": True,
}

USER_EMPLOYEE = {
    "name": "Bob Employee",
    "email": "bob.employee@example.com",
    "role": UserRole.STAFF.value,
    "hashed_pw": "Empl@yee123",
    "department_id": 20,
    "admin": False,
}
