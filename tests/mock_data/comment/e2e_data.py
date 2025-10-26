# tests/mock_data/comment/e2e_data.py
from backend.src.enums.task_status import TaskStatus
from backend.src.enums.user_role import UserRole
from datetime import date, timedelta

E2E_COMMENT_WORKFLOW = {
    "entity_ids": {
        "task_id": 1,
        "user_id": 1,
        "project_id": 1,
    },
    "user": {
        "email": "tester@example.com",
        "name": "Tester",
        "role": UserRole.STAFF.value,
        "admin": False,
        "hashed_pw": "x",
    },
    "project": {
        "project_name": "Project Alpha",
        "active": True,
    },
    "task": {
        "title": "Default Task",
        "description": None,
        "status": TaskStatus.TO_DO.value,
        "priority": 5,
        "active": True,
        "recurring": False,
    },
    "comments": {
        "create": "Initial test comment",
        "update": "Updated comment text",
    },
    "expected_messages": {
        "create_success": "comment added successfully",
        "update_success": "comment updated successfully",
        "delete_success": "comment deleted successfully",
    },
}

E2E_SELECTORS = {
    "comment_item": ".comment-item",
    "comment_input": "commentInput",
    "submit_button": "submitComment",
    "refresh_button": "refresh",
    "status_element": "status",
    "update_button": ".btn-update",
    "update_input": ".update-input",
    "save_button": ".btn-save",
    "delete_button": ".btn-delete",
}

VALID_PROJECT = {
    "project_id": 1,
    "project_name": "Project Alpha",
    "project_manager": 1,
    "active": True,
}

VALID_TASK = {
    "id": 1,
    "title": "Default Task",
    "description": None,
    "status": TaskStatus.TO_DO.value,
    "start_date": (date.today() + timedelta(days=3)),
    "deadline": (date.today() + timedelta(days=10)),
    "priority": 5,
    "project_id": 1,
    "active": True,
}

VALID_USER = {
    "user_id": 1,
    "email": "tester@example.com",
    "name": "Tester",
    "role": UserRole.STAFF.value,
    "admin": False,
    "hashed_pw": "hashed_pw",
    "department_id": None,
}
