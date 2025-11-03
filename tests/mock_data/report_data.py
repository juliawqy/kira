"""
Mock data for report service unit tests.
Uses JSON/dictionary structures for all mock data.
"""
from datetime import date
from backend.src.enums.task_status import TaskStatus
from backend.src.enums.user_role import UserRole


MOCK_USER_MANAGER = {
    "name": "Project Manager",
    "email": "manager@test.com",
    "role": UserRole.MANAGER.value,
    "hashed_pw": "hashed_pw",
    "admin": False,
    "department_id": None
}

MOCK_USER_TEAM_MEMBER_1 = {
    "name": "Team Member 1",
    "email": "member1@test.com",
    "role": UserRole.STAFF.value,
    "hashed_pw": "hashed_pw",
    "admin": False,
    "department_id": None
}

MOCK_USER_TEAM_MEMBER_2 = {
    "name": "Team Member 2",
    "email": "member2@test.com",
    "role": UserRole.STAFF.value,
    "hashed_pw": "hashed_pw",
    "admin": False,
    "department_id": None
}

MOCK_USERS = [
    MOCK_USER_MANAGER,
    MOCK_USER_TEAM_MEMBER_1,
    MOCK_USER_TEAM_MEMBER_2
]

MOCK_USER_BY_NAME = {
    "Project Manager": MOCK_USER_MANAGER,
    "Team Member 1": MOCK_USER_TEAM_MEMBER_1,
    "Team Member 2": MOCK_USER_TEAM_MEMBER_2
}

MOCK_PROJECT = {
    "project_id": 1,
    "project_name": "Test Project Report",
    "project_manager": 1,
    "active": True
}

MOCK_PROJECT_MINIMAL = {
    "project_name": "Minimal Project"
}

INVALID_PROJECT_EMPTY = {}

INVALID_PROJECT_NO_NAME = {
    "project_id": 1,
    "project_manager": 1
}

MOCK_TASK_TO_DO = {
    "id": 1,
    "title": "Projected Task 1",
    "description": "A task that hasn't started yet",
    "status": TaskStatus.TO_DO.value,
    "priority": 7,
    "start_date": date(2024, 12, 1),
    "deadline": date(2024, 12, 15),
    "tag": "feature",
    "project_id": 1,
    "active": True
}

MOCK_TASK_IN_PROGRESS = {
    "id": 2,
    "title": "In-Progress Task",
    "description": "Currently being worked on",
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 9,
    "start_date": date(2024, 11, 20),
    "deadline": date(2024, 12, 10),
    "tag": "bugfix",
    "project_id": 1,
    "active": True
}

MOCK_TASK_COMPLETED = {
    "id": 3,
    "title": "Completed Task",
    "description": "Finished successfully",
    "status": TaskStatus.COMPLETED.value,
    "priority": 6,
    "start_date": date(2024, 11, 1),
    "deadline": date(2024, 11, 15),
    "tag": "feature",
    "project_id": 1,
    "active": True
}

MOCK_TASK_BLOCKED = {
    "id": 4,
    "title": "Under Review Task",
    "description": "Blocked and needs review",
    "status": TaskStatus.BLOCKED.value,
    "priority": 8,
    "start_date": date(2024, 11, 15),
    "deadline": date(2024, 12, 5),
    "tag": "blocked",
    "project_id": 1,
    "active": True
}

MOCK_TASK_TO_DO_2 = {
    "id": 7,
    "title": "Projected Task 2",
    "description": "Another planned task",
    "status": TaskStatus.TO_DO.value,
    "priority": 5,
    "start_date": date(2024, 12, 5),
    "deadline": date(2024, 12, 20),
    "tag": "enhancement",
    "project_id": 1,
    "active": True
}

MOCK_TASK_COMPLETED_2 = {
    "id": 8,
    "title": "Completed Task 2",
    "description": "Another completed task",
    "status": TaskStatus.COMPLETED.value,
    "priority": 4,
    "start_date": date(2024, 11, 5),
    "deadline": date(2024, 11, 20),
    "tag": "documentation",
    "project_id": 1,
    "active": True
}

MOCK_TASK_NO_DATES = {
    "id": 5,
    "title": "Task Without Dates",
    "description": "Task with no start or deadline",
    "status": TaskStatus.TO_DO.value,
    "priority": 3,
    "start_date": None,
    "deadline": None,
    "tag": None,
    "project_id": 1,
    "active": True
}

MOCK_TASK_LONG_TITLE = {
    "id": 7,
    "title": "This is a very long task title that exceeds forty characters in length for testing truncation",
    "description": "Testing long title truncation",
    "status": TaskStatus.IN_PROGRESS.value,
    "priority": 5,
    "start_date": date(2024, 12, 1),
    "deadline": date(2024, 12, 20),
    "tag": None,
    "project_id": 1,
    "active": True
}

MOCK_TASKS_ALL_STATUSES = [
    MOCK_TASK_TO_DO,
    MOCK_TASK_IN_PROGRESS,
    MOCK_TASK_COMPLETED,
    MOCK_TASK_BLOCKED
]

MOCK_TASKS_EMPTY = []

MOCK_TASKS_WITH_NULLS = [
    MOCK_TASK_NO_DATES,
    MOCK_TASK_TO_DO
]

MOCK_TASK_ASSIGNEES = {
    1: ["Team Member 1"], 
    2: ["Team Member 1", "Team Member 2"],  
    3: ["Project Manager"],  
    4: [],  
    5: [],  
    6: ["Single Assignee"],  
    7: ["Team Member 1"],  
    8: [],  
}

MOCK_TASK_ASSIGNEES_EMPTY = {}

MOCK_TASK_ASSIGNEES_ALL_UNASSIGNED = {
    1: [],
    2: [],
    3: [],
    4: []
}

