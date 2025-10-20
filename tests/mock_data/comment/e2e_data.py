# tests/mock_data/comment/e2e_data.py

E2E_COMMENT_WORKFLOW = {
    "entity_ids": {
        "task_id": 1,
        "user_id": 2,
        "project_id": 1,
    },
    "user": {
        "email": "testuser@example.com",
        "name": "Test User",
        "role": "STAFF",
        "admin": False,
        "hashed_pw": "x",
    },
    "project": {
        "project_name": "UI Test Project",
        "active": True,
    },
    "task": {
        "title": "Test Task",
        "description": "Task used for comment testing",
        "status": "To-do",
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
