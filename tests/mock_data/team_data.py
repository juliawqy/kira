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

HR_USER = {
    "user_id": 4,
    "name": "HR User",
    "email": "hr@example.com",
    "role": UserRole.HR.value,
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

VALID_DEPARTMENT = {
    "department_id": 1,
    "department_name": "Engineering",
    "manager_id": 1,
}

INVALID_USER_ID = 99999

VALID_TEAM_CREATE = {
    "team_name": "Cong is the baddie",
    "manager_id": 2,
    "department_id": 1,
}

VALID_TEAM = {
    "team_id": 1,
    "team_name": "Cong is the baddie",
    "manager_id": 2,
    "department_id": 1,
    "team_number": "010100",
}

VALID_SUBTEAM_CREATE = {
    "team_id": 1,
    "team_name": "Subteam Alpha",
    "manager_id": 2,
}

VALID_SUBTEAM = {
    "team_id": 2,
    "team_name": "Subteam Alpha",
    "manager_id": 2,
    "department_id": 1,
    "team_number": "010102",
}

INVALID_CREATE_INVALID_DEPARTMENT_ID = {
    "team_name": "Invalid Dept Team",
    "manager_id": 2,
    "department_id": 9999,
}

INVALID_CREATE_INVALID_TEAM_ID = {
    "team_name": "Invalid Subteam",
    "manager_id": 2,
    "team_id": 9999,
}

INVALID_CREATE_INVALID_MANAGER_ID = {
    "team_name": "Invalid Manager Team",
    "manager_id": 9999,
    "department_id": 1,
}

INVALID_CREATE_INVALID_SUBTEAM_MANAGER_ID = {
    "team_name": "Invalid Subteam Manager",
    "manager_id": 9999,
    "team_id": 1,
}

INVALID_CREATE_TEAM_UNAUTHORISED = {
    "team_name": "Invalid Team Manager",
    "manager_id": 1,
    "department_id": 1,
}

INVALID_CREATE_SUBTEAM_UNAUTHORISED = {
    "team_name": "Invalid Subteam Manager",
    "manager_id": 1,
    "team_id": 1,
}

NOT_FOUND_ID = 9999
INVALID_TEAM_NUMBER = "999999"


