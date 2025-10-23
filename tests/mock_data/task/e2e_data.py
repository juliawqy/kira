from backend.src.enums.task_status import TaskStatus
from backend.src.enums.user_role import UserRole

E2E_TASK_WORKFLOW = {
    "create": {
        "title": "Initial Task",
        "description": "This is a test task",
        "priority": 5,
        "status": TaskStatus.TO_DO.value,
        "project_id": 1,
    },
    "update": {
        "title": "Updated Task Title",
        "description": "This task was updated",
        "priority": 8,
        "project_id": 2
    },
    "expected_responses": {
        "create_success": "task created",
        "update_success": ["updated successfully", "task updated"],
        "delete_success": ["deleted successfully", "task removed"],
    }
}

E2E_SELECTORS = {
    "list_view": {
        "task_items": ".task-item",
        "task_info": ".task-info",
        "update_button": ".update-btn",
        "delete_button": ".delete-btn",
        "parent_delete_button": ".parent-delete-btn",  # new
        "save_button": ".save-btn",
        "attach_button": ".attach-btn",
        "detach_buttons": ".detach-btn",
        "subtask_badge": ".subtask-item",
    },
    "forms": {
        "title_input": "task-title",
        "description_input": "task-desc",
        "priority_input": "task-priority",
        "status_select": "task-status",
        "project_input": "task-project",
        "submit_button": "#create-task",
        "attach_input_prefix": "attach-input-",  # use [id^='attach-input-']
    },
    "status": {
        "status_element": "status-msg",
        "refresh_button": "refresh-btn",
    }
}

VALID_PROJECT = {
    "project_id": 1,
    "project_name": "Project Alpha",
    "project_manager": 1,
    "active": True,
}

VALID_PROJECT_2 = {
    "project_id": 2,
    "project_name": "Project Beta",
    "project_manager": 1,
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