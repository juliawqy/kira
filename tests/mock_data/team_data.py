from backend.src.enums.user_role import UserRole


STAFF_USER = {
    "user_id": 2,
    "name": "Zoom Zoom",
    "email": "zoomzoom@smu.edu.sg",
    "role": UserRole.STAFF.value,
}

DIRECTOR_USER = {
    "user_id": 3,
    "name": "Director User",
    "email": "boss@example.com",
    "role": "Director",
}

NO_ROLE_USER = {
    "user_id": 60,
    "name": "No Role User",
    "email": "norole@example.com",
}

VALID_TEAM_CREATE = {
    "team_id": 1,
    "team_name": "Cong is the baddie",
    "manager_id": 42,
    "department_id": 10,
    "team_number": 5,
}

INVALID_TEAM_EMPTY = {
    "team_name": "",
}

INVALID_TEAM_WHITESPACE = {
    "team_name": "   ",
}

MANAGER_USER = {
    "user_id": 1,
    "name": "Manager User",
    "email": "manager@example.com",
    "role": UserRole.MANAGER.value,
}


DIRECTOR_USER = {
    "user_id": 3,
    "name": "Director User",
    "email": "boss@example.com",
    "role": UserRole.DIRECTOR.value,
}


NO_ROLE_USER = {
    "user_id": 60,
    "name": "No Role User",
    "email": "norole@example.com",
}

NOT_FOUND_ID = 9999

# Common assignee ids used in integration tests
ASSIGNEE_ID_123 = 123
ASSIGNEE_ID_222 = 222
ASSIGNEE_ID_55 = 55
ASSIGNEE_ID_999 = 999

# Common team ids used in tests
TEAM_ID_1 = 1
TEAM_ID_2 = 2
TEAM_ID_3 = 3
TEAM_ID_42 = 42
TEAM_ID_77 = 77

