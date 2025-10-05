STAFF_USER = {
    "user_id": 2,
    "name": "Zoom Zoom",
    "email": "zoomzoom@smu.edu.sg",
    "role": "Staff",
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
    "role": "Manager",
}

# Id used in tests to represent a missing resource
NOT_FOUND_ID = 9999

