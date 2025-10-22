from backend.src.enums.user_role import UserRole


STAFF_USER = {
    "user_id": 1,
    "email": "tester@example.com",
    "name": "Tester",
    "role": UserRole.STAFF.value,
    "admin": False,
    "hashed_pw": "hashed_pw",
    "department_id": None,
}

MANAGER_USER = {
    "user_id": 2,
    "name": "Manager User",
    "email": "manager@example.com",
    "role": UserRole.MANAGER.value,
    "admin": False,
    "hashed_pw": "hashed_pw",
    "department_id": None,
}

DIRECTOR_USER = {
    "user_id": 3,
    "name": "Director User",
    "email": "boss@example.com",
    "role": UserRole.DIRECTOR.value,
    "admin": False,
    "hashed_pw": "hashed_pw",
    "department_id": None,
}

INVALID_USER_ID = 99999

VALID_TEAM_CREATE = {
    "team_id": 1,
    "team_name": "Cong is the baddie",
    "manager_id": 2,
    "department_id": 1,
    "team_number": 1,
}


NO_ROLE_USER = {
    "user_id": 60,
    "name": "No Role User",
    "email": "norole@example.com",
}

NOT_FOUND_ID = 9999

# Common team ids used in tests
TEAM_ID_1 = 1
TEAM_ID_2 = 2
TEAM_ID_3 = 3
TEAM_ID_42 = 42
TEAM_ID_77 = 77

