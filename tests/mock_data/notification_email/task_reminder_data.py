"""Mock data for task reminder integration tests (upcoming_task_reminder and overdue_task_reminder)."""

from backend.src.enums.user_role import UserRole


# =============================================================================
# TASK FACTORY DATA
# =============================================================================

UPCOMING_TASK = {
    "title": "Upcoming Deadline Task",
    "description": "Test task for upcoming deadline reminder",
    "priority": 5,
    "project_id": 1,
    "deadline": "2025-12-25",  # Will be parsed as date
}

OVERDUE_TASK = {
    "title": "Overdue Task",
    "description": "Test task for overdue reminder",
    "priority": 8,
    "project_id": 1,
    "deadline": "2024-01-01",  # Past date
}

TASK_WITHOUT_DEADLINE = {
    "title": "Task Without Deadline",
    "description": "Test task without deadline",
    "priority": 3,
    "project_id": 1,
}

TASK_WITH_PROJECT = {
    "title": "Task with Project",
    "description": "Test task with project info",
    "priority": 7,
    "project_id": 1,
    "deadline": "2025-12-25",
}


# =============================================================================
# RECIPIENT/SCENARIO MOCK DATA (recipient-based, not assignee-based)
# =============================================================================

# Users with complete information including emails (success scenarios)
ASSIGNEES_WITH_EMAILS = [
    {
        "user_id": 101,
        "name": "John Doe", 
        "email": "john.doe@example.com",
        "role": UserRole.STAFF.value,
        "department_id": 1,
        "admin": False,
    },
    {
        "user_id": 102,
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "role": UserRole.MANAGER.value,
        "department_id": 1,
        "admin": False,
    },
]

# Single assignee for simple tests
SINGLE_ASSIGNEE_WITH_EMAIL = [
    {
        "user_id": 101,
        "name": "Test User",
        "email": "test.user@example.com",
        "role": UserRole.STAFF.value,
        "department_id": 1,
        "admin": False,
    }
]

# Mixed scenario data
MIXED_EMAIL_ASSIGNEES_SUCCESS = {
    "task_data": UPCOMING_TASK,
    "assignees_with_emails": [
        {
            "user_id": 101,
            "name": "John Doe",
            "email": "john.doe@example.com", 
            "role": UserRole.STAFF.value,
            "department_id": 1,
            "admin": False,
        },
        {
            "user_id": 103,
            "name": "Bob Wilson",
            "email": "bob.wilson@example.com",
            "role": UserRole.MANAGER.value,
            "department_id": 1,
            "admin": False,
        },
    ],
    "assignees_without_emails": [
        {
            "user_id": 102,
            "name": "Jane Smith",
            "role": UserRole.MANAGER.value,
            "department_id": 1,
            "admin": False,
        },
    ],
    "expected_recipients_count": 2,
    "expected_response": {
        "success": True,
        "recipients_count": 2,
    }
}


# =============================================================================
# NO RECIPIENTS SCENARIOS
# =============================================================================

NO_RECIPIENTS_SCENARIO_EMPTY = {
    "task_data": UPCOMING_TASK,
    "expected_response": {
        "success": True,
        "message": "No recipients configured for notifications",
        "recipients_count": 0,
    },
    "expected_smtp_calls": False,
}

NO_RECIPIENTS_SCENARIO_NO_EMAILS = {
    "task_data": UPCOMING_TASK,
    "expected_response": {
        "success": True,
        "message": "No recipients configured for notifications", 
        "recipients_count": 0,
    },
    "expected_smtp_calls": False,
}


# =============================================================================
# ERROR SCENARIOS
# =============================================================================

ERROR_SCENARIO_TASK_NOT_FOUND = {
    "task_id": 999999,
    "mock_task_service_return": None,
    "expected_exception": {
        "status_code": 404,
        "detail_contains": ["Task not found"],
    },
}

ERROR_SCENARIO_NO_DEADLINE = {
    "task_data": TASK_WITHOUT_DEADLINE,
    "expected_response": {
        "success": False,
        "message": "Task does not have a deadline",
        "recipients_count": 0,
    },
    "expected_smtp_calls": False,
}

ERROR_SCENARIO_SEND_FAILURE = {
    "task_data": UPCOMING_TASK,
    "expected_exception": {
        "status_code": 500,
        "detail_contains": ["Error sending notification"],
    },
}


# =============================================================================
# SUCCESS SCENARIOS
# =============================================================================

SUCCESS_SCENARIO_UPCOMING_SINGLE = {
    "task_data": UPCOMING_TASK,
    "expected_response": {
        "success": True,
        "recipients_count": 1,
    },
    "expected_smtp_calls": ["starttls", "quit"],
}

SUCCESS_SCENARIO_UPCOMING_MULTIPLE = {
    "task_data": UPCOMING_TASK,
    "expected_response": {
        "success": True,
        "recipients_count": 2,
    },
    "expected_smtp_calls": ["starttls", "quit"],
}

SUCCESS_SCENARIO_OVERDUE_SINGLE = {
    "task_data": OVERDUE_TASK,
    "expected_response": {
        "success": True,
        "recipients_count": 1,
    },
    "expected_smtp_calls": ["starttls", "quit"],
}

SUCCESS_SCENARIO_OVERDUE_MULTIPLE = {
    "task_data": OVERDUE_TASK,
    "expected_response": {
        "success": True,
        "recipients_count": 2,
    },
    "expected_smtp_calls": ["starttls", "quit"],
}


# =============================================================================
# COMPREHENSIVE SCENARIO COLLECTIONS
# =============================================================================

ALL_UPCOMING_SUCCESS_SCENARIOS = {
    "single_assignee": SUCCESS_SCENARIO_UPCOMING_SINGLE,
    "multiple_assignees": SUCCESS_SCENARIO_UPCOMING_MULTIPLE,
    "mixed_emails": MIXED_EMAIL_ASSIGNEES_SUCCESS,
}

ALL_OVERDUE_SUCCESS_SCENARIOS = {
    "single_assignee": SUCCESS_SCENARIO_OVERDUE_SINGLE,
    "multiple_assignees": SUCCESS_SCENARIO_OVERDUE_MULTIPLE,
}

ALL_NO_RECIPIENTS_SCENARIOS = {
    "empty_assignees": NO_RECIPIENTS_SCENARIO_EMPTY,
    "no_email_addresses": NO_RECIPIENTS_SCENARIO_NO_EMAILS,
}

ALL_ERROR_SCENARIOS = {
    "task_not_found": ERROR_SCENARIO_TASK_NOT_FOUND,
    "no_deadline": ERROR_SCENARIO_NO_DEADLINE,
    "send_failure": ERROR_SCENARIO_SEND_FAILURE,
}
# Additional simple alias for tests
RECIPIENTS_SUCCESS_TWO = {
    "expected_response": {
        "success": True,
        "recipients_count": 2,
    }
}


# =============================================================================
# HELPER FUNCTIONS FOR MOCK USER CREATION
# =============================================================================

def create_user_with_email(**kwargs):
    """Create a user object with email attribute."""
    return type('UserWithEmail', (), {
        'user_id': kwargs.get('user_id'),
        'name': kwargs.get('name'),
        'email': kwargs.get('email'),
        'role': kwargs.get('role'),
        'department_id': kwargs.get('department_id'),
        'admin': kwargs.get('admin', False),
    })()

def create_user_without_email(**kwargs):
    """Create a user object without email attribute."""
    return type('UserWithoutEmail', (), {
        'user_id': kwargs.get('user_id'),
        'name': kwargs.get('name'),
        'role': kwargs.get('role'), 
        'department_id': kwargs.get('department_id'),
        'admin': kwargs.get('admin', False),
    })()

