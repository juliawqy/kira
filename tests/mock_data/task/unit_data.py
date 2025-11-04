from datetime import date, timedelta
from backend.src.enums.task_status import TaskStatus
from backend.src.enums.user_role import UserRole

VALID_DEFAULT_TASK = {
    "id": 1,
    "title": "Default Task",
    "description": None,
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "recurring": 0,
    "project_id": 123,
    "active": True,
}

VALID_TASK_EXPLICIT_PRIORITY = {
    "id": 2,
    "title": "Task with Explicit Priority",
    "description": None,
    "start_date": None, 
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 8,
    "recurring": 0,
    "project_id": 100,
    "active": True,
}

VALID_TASK_FULL = {
    "id": 3,
    "title": "Full Task Details",
    "description": "Complete task with all fields",
    "start_date": date.today(),
    "deadline": date.today() + timedelta(days=7),
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 9,
    "recurring": 0,
    "project_id": 123,
    "active": True,
}

INACTIVE_TASK = {
    "id": 4,
    "title": "Inactive Task",
    "description": "This task is inactive",
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "recurring": 0,
    "project_id": 100,
    "active": False,
}

VALID_TASK_TODO = {
    "id": 1,
    "title": "Complete user authentication",
    "description": "Implement login and registration system",
    "start_date": date.today() + timedelta(days=1),
    "deadline": date.today() + timedelta(days=7),
    "status": TaskStatus.TO_DO.value,
    "priority": 8,
    "recurring": 0,
    "project_id": 100,
    "active": True,
}

VALID_TASK_IN_PROGRESS = {
    "id": 2,
    "title": "Database migration",
    "description": "Migrate from SQLite to PostgreSQL",
    "start_date": date.today() - timedelta(days=2),
    "deadline": date.today() + timedelta(days=14),
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 9,
    "recurring": 0,
    "project_id": 100,
    "active": True,
}

VALID_TASK_COMPLETED = {
    "id": 3,
    "title": "Setup CI/CD pipeline",
    "description": "Configure GitHub Actions for automated testing",
    "start_date": date.today() - timedelta(days=10),
    "deadline": date.today() - timedelta(days=3),
    "status": TaskStatus.COMPLETED.value,
    "priority": 6,
    "recurring": 0,
    "project_id": 101,
    "active": True,
}

VALID_TASK_BLOCKED = {
    "id": 4,
    "title": "Performance optimization",
    "description": "Optimize database queries",
    "start_date": date.today() - timedelta(days=10),
    "deadline": date.today() + timedelta(days=14),
    "status": TaskStatus.BLOCKED.value,
    "priority": 5,
    "recurring": 0,
    "project_id": 102,
    "active": True,
}

# Create

VALID_CREATE_PAYLOAD_MINIMAL = {
    "title": "Default Task",
    "project_id": 123
}

VALID_CREATE_PAYLOAD_WITH_EXPLICIT_PRIORITY = {
    "title": "Task with Explicit Priority",
    "priority": 8, 
    "project_id": 100,
}

VALID_CREATE_PAYLOAD_FULL = {
    "title": "Full Task Details",
    "description": "Complete task with all fields",
    "start_date": date.today(),
    "deadline": date.today() + timedelta(days=7),
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 9,
    "recurring": 0,
    "tag": None,
    "project_id": 123,
    "active": True,
}

# Update

VALID_UPDATE_DEFAULT_TASK = {
    "id": 1,
    "title": "Updated Task Title",
    "description": "Updated description",
    "start_date": date.today() + timedelta(days=1),
    "deadline": date.today() + timedelta(days=14),
    "status": TaskStatus.TO_DO.value,
    "priority": 8,
    "recurring": 0,
    "project_id": 123,
    "active": True,
}

VALID_UPDATE_PAYLOAD = {
    "title": "Updated Task Title",
    "description": "Updated description",
    "priority": 8,
    "start_date": date.today() + timedelta(days=1),
    "deadline": date.today() + timedelta(days=14),
}

EMPTY_UPDATE_PAYLOAD = {
    "title": None,
    "description": None,
    "priority": None,
    "start_date": None,
    "deadline": None,
}

INVALID_UPDATE_PAYLOAD_WITH_STATUS = {
    "title": "Updated Task Title",
    "description": "Updated description",
    "priority": 8,
    "start_date": date.today() + timedelta(days=1),
    "deadline": date.today() + timedelta(days=14),
    "status": "COMPLETED"
}

INVALID_UPDATE_PAYLOAD_WITH_ACTIVE = {
    "title": "Updated Task Title",
    "description": "Updated description",
    "priority": 8,
    "start_date": date.today() + timedelta(days=1),
    "deadline": date.today() + timedelta(days=14),
    "active" : False
}

INVALID_UPDATE_PAYLOAD_WITH_STATUS_AND_ACTIVE = {
    "title": "Updated Task Title",
    "description": "Updated description",
    "priority": 8,
    "start_date": date.today() + timedelta(days=1),
    "deadline": date.today() + timedelta(days=14),
    "status": "COMPLETED",
    "active" : False
}

# Valid test values
VALID_PROJECT_ID = 123
VALID_PROJECT_ID_INACTIVE_TASK = 100

# Invalid test data for parameterized tests
INVALID_PRIORITIES = [-1, 0, 11, "High", None]
INVALID_PRIORITY_VALUES = [-1, 0, 11, 999]  
INVALID_PRIORITY_TYPES = ["High", 3.14, [], {}] 
INVALID_STATUSES = ["In progress", "DONE", "Todo", None, "", 123]
INVALID_TASK_ID_NONEXISTENT = 99999
EMPTY_PROJECT_ID = 99999

# Edge cases
EDGE_CASE_PRIORITY_BOUNDARY_LOW = {"priority": 1}  # Minimum valid
EDGE_CASE_PRIORITY_BOUNDARY_HIGH = {"priority": 10}  # Maximum valid

# Parent task 
VALID_PARENT_TASK = {
    "id": 10,
    "title": "Parent Task",
    "description": "Main task with subtasks",
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 6,
    "recurring": 0,
    "project_id": 100,
    "active": True,
}

INACTIVE_PARENT_TASK = {
    "id": 11,
    "title": "Inactive Parent",
    "description": "Parent task that is archived",
    "start_date": None,
    "deadline": None,
    "status": TaskStatus.TO_DO.value,
    "priority": 7,
    "recurring": 0,
    "project_id": 100,
    "active": False,
}

INVALID_PARENT_IDS = [0, -1]

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

VALID_USER_DIRECTOR = {
    "user_id": 3,
    "name": "Charlie Director",
    "email": "charlie.director@example.com",
    "role": UserRole.DIRECTOR.value,
    "department_id": 30,
    "admin": False,
    "password": "Dir3ct0rPass!",
}

INVALID_USER_ID = 9999

VALID_TEAM = {
    "team_id": 1,
    "team_number": "010100",
    "manager_id": 2,
    "team_name": "Development Team",
    "department_id": 1,
}

VALID_SUBTEAM = {
    "team_id": 2,
    "team_number": "010102",
    "manager_id": 2,
    "team_name": "Development Subteam",
    "department_id": 1,
}