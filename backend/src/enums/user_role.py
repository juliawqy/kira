from enum import Enum

class UserRole(str, Enum):

    STAFF = "Staff"
    MANAGER = "Manager"
    DIRECTOR = "Director"
    HR = "HR"

ALLOWED_ROLES = {r.value for r in UserRole}