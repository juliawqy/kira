"""Mock data for notify_task_assignees integration tests following the established pattern."""

from backend.src.enums.user_role import UserRole
from backend.src.enums.notification import NotificationType


# =============================================================================
# TASK FACTORY DATA (following existing pattern)
# =============================================================================

NOTIFY_ASSIGNEES_TASK_INITIAL = {
    "title": "Notify Assignees Test Task",
    "description": "Test task for notify assignees functionality",
    "priority": 5,
    "project_id": 1,
}

NOTIFY_ASSIGNEES_TASK_MIXED = {
    "title": "Mixed Email Availability Task",
    "description": "Test task with mixed assignees",
    "priority": 3,
    "project_id": 1,
}


# =============================================================================
# ASSIGNEE MOCK DATA (following existing user patterns)
# =============================================================================

# Users with complete information including emails (success scenarios)
ASSIGNEES_WITH_EMAILS = [
    {
        "user_id": 1,
        "name": "John Doe", 
        "email": "john.doe@example.com",
        "role": UserRole.DEVELOPER.value,
        "department_id": 1,
        "admin": False,
    },
    {
        "user_id": 2,
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "role": UserRole.TESTER.value,
        "department_id": 1,
        "admin": False,
    },
]

# Single assignee for simple tests
SINGLE_ASSIGNEE_WITH_EMAIL = [
    {
        "user_id": 1,
        "name": "Test User",
        "email": "test.user@example.com",
        "role": UserRole.DEVELOPER.value,
        "department_id": 1,
        "admin": False,
    }
]

# Mixed scenario data (following integration test pattern)
MIXED_EMAIL_ASSIGNEES_SUCCESS = {
    "task_data": NOTIFY_ASSIGNEES_TASK_MIXED,
    "assignees_with_emails": [
        {
            "user_id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com", 
            "role": UserRole.DEVELOPER.value,
            "department_id": 1,
            "admin": False,
        },
        {
            "user_id": 3,
            "name": "Bob Wilson",
            "email": "bob.wilson@example.com",
            "role": UserRole.MANAGER.value,
            "department_id": 1,
            "admin": False,
        },
    ],
    "assignees_without_emails": [
        {
            "user_id": 2,
            "name": "Jane Smith",
            "role": UserRole.TESTER.value,
            "department_id": 1,
            "admin": False,
            # Note: No email attribute
        },
        {
            "user_id": 4,
            "name": "Alice Brown",
            "role": UserRole.DESIGNER.value,
            "department_id": 1,
            "admin": False,
            # Note: No email attribute
        },
    ],
    "expected_recipients_count": 2,  # Only users with emails
    "expected_response": {
        "success": True,
        "recipients_count": 2,
    }
}

# No recipients scenarios (following existing pattern)
NO_RECIPIENTS_SCENARIO_EMPTY = {
    "task_data": NOTIFY_ASSIGNEES_TASK_INITIAL,
    "assignees": [],
    "expected_response": {
        "success": True,
        "message": "No assigned users with email addresses found",
        "recipients_count": 0,
    },
    "expected_smtp_calls": False,  # No SMTP calls expected
}

NO_RECIPIENTS_SCENARIO_NO_EMAILS = {
    "task_data": NOTIFY_ASSIGNEES_TASK_INITIAL,
    "assignees": [
        {
            "user_id": 1,
            "name": "John Doe",
            "role": UserRole.DEVELOPER.value,
            "department_id": 1,
            "admin": False,
            # Note: No email attribute
        }
    ],
    "expected_response": {
        "success": True,
        "message": "No assigned users with email addresses found", 
        "recipients_count": 0,
    },
    "expected_smtp_calls": False,  # No SMTP calls expected
}


# =============================================================================
# ERROR SCENARIOS (following existing error handling pattern)
# =============================================================================

ERROR_SCENARIO_TASK_NOT_FOUND = {
    "task_id": 999999,  # Non-existent task
    "mock_task_service_return": None,  # Simulate task not found
    "message": "Test message",
    "alert_type": NotificationType.TASK_UPDATE.value,
    "expected_exception": {
        "status_code": 500,
        "detail_contains": ["Error sending notification", "404: Task not found"],
    },
}

ERROR_SCENARIO_INVALID_ALERT_TYPE = {
    "task_data": NOTIFY_ASSIGNEES_TASK_INITIAL,
    "assignees": SINGLE_ASSIGNEE_WITH_EMAIL,
    "message": "Test message",
    "alert_type": "invalid_alert_type",
    "expected_exception": {
        "status_code": 500,
        "detail_contains": ["Error sending notification", "400: Invalid type_of_alert", "task_create"],
    },
}

ERROR_SCENARIO_ASSIGNMENT_SERVICE = {
    "task_data": NOTIFY_ASSIGNEES_TASK_INITIAL,
    "assignment_service_error": ValueError("Assignment service error"),
    "message": "Test message", 
    "alert_type": NotificationType.TASK_UPDATE.value,
    "expected_exception": {
        "status_code": 404,
        "detail_contains": ["Assignment service error"],
    },
}

ERROR_SCENARIO_NOTIFICATION_SERVICE = {
    "task_data": NOTIFY_ASSIGNEES_TASK_INITIAL,
    "assignees": SINGLE_ASSIGNEE_WITH_EMAIL,
    "notification_service_error": Exception("Notification service explosion"),
    "message": "Test message",
    "alert_type": NotificationType.TASK_UPDATE.value,
    "expected_exception": {
        "status_code": 500,
        "detail_contains": ["Error sending notification", "Notification service explosion"],
    },
}

ERROR_SCENARIO_COMMENT_VALIDATION = {
    "task_data": NOTIFY_ASSIGNEES_TASK_INITIAL,
    "assignees": SINGLE_ASSIGNEE_WITH_EMAIL,
    "message": "Test message",
    "alert_type": NotificationType.COMMENT_CREATE.value,  # Requires comment_user
    "expected_response": {
        "success": False,
        "message_contains": ["Notification service error", "comment_user is required for comment-related alerts"],
        "recipients_count": 0,
    },
    "expected_smtp_calls": False,  # No SMTP calls due to validation failure
}


# =============================================================================
# SUCCESS SCENARIOS (following existing success pattern)
# =============================================================================

SUCCESS_SCENARIO_SINGLE_ASSIGNEE = {
    "task_data": NOTIFY_ASSIGNEES_TASK_INITIAL,
    "assignees": SINGLE_ASSIGNEE_WITH_EMAIL,
    "message": "Custom test message",
    "alert_type": NotificationType.TASK_UPDATE.value,
    "expected_response": {
        "success": True,
        "recipients_count": 1,
    },
    "expected_smtp_calls": ["starttls", "login", "send_message", "quit"],
}

SUCCESS_SCENARIO_MULTIPLE_ASSIGNEES = {
    "task_data": NOTIFY_ASSIGNEES_TASK_INITIAL,
    "assignees": ASSIGNEES_WITH_EMAILS,
    "message": "Multiple assignees test",
    "alert_type": NotificationType.TASK_ASSGN.value,
    "expected_response": {
        "success": True,
        "recipients_count": 2,
    },
    "expected_smtp_calls": ["starttls", "login", "send_message", "quit"],
}

SUCCESS_SCENARIO_DEFAULT_PARAMETERS = {
    "task_data": NOTIFY_ASSIGNEES_TASK_INITIAL,
    "assignees": SINGLE_ASSIGNEE_WITH_EMAIL,
    "message": None,  # Use default
    "alert_type": None,  # Use default
    "expected_defaults": {
        "message": "Task update notification",
        "alert_type": "task_update",
    },
    "expected_response": {
        "success": True,
        "recipients_count": 1,
    },
    "expected_smtp_calls": ["starttls", "login", "send_message", "quit"],
}


# =============================================================================
# ALERT TYPE VALIDATION DATA
# =============================================================================

VALID_NON_COMMENT_ALERT_TYPES = [
    NotificationType.TASK_CREATE.value,
    NotificationType.TASK_UPDATE.value,
    NotificationType.TASK_ASSIGN.value,
    NotificationType.TASK_UNASSIGN.value,
    NotificationType.DELETE_TASK.value,
    NotificationType.DELETE_COMMENT.value,
]

COMMENT_ALERT_TYPES_REQUIRING_USER = [
    NotificationType.COMMENT_CREATE.value,
    NotificationType.COMMENT_MENTION.value,
    NotificationType.COMMENT_UPDATE.value,
]

INVALID_ALERT_TYPES = [
    "invalid_alert_type",
    "non_existent_type",
    "random_string",
]


# =============================================================================
# COMPREHENSIVE SCENARIO COLLECTIONS (following existing pattern)
# =============================================================================

ALL_SUCCESS_SCENARIOS = {
    "single_assignee": SUCCESS_SCENARIO_SINGLE_ASSIGNEE,
    "multiple_assignees": SUCCESS_SCENARIO_MULTIPLE_ASSIGNEES,
    "mixed_emails": MIXED_EMAIL_ASSIGNEES_SUCCESS,
    "default_parameters": SUCCESS_SCENARIO_DEFAULT_PARAMETERS,
}

ALL_NO_RECIPIENTS_SCENARIOS = {
    "empty_assignees": NO_RECIPIENTS_SCENARIO_EMPTY,
    "no_email_addresses": NO_RECIPIENTS_SCENARIO_NO_EMAILS,
}

ALL_ERROR_SCENARIOS = {
    "task_not_found": ERROR_SCENARIO_TASK_NOT_FOUND,
    "invalid_alert_type": ERROR_SCENARIO_INVALID_ALERT_TYPE,
    "assignment_service_error": ERROR_SCENARIO_ASSIGNMENT_SERVICE,
    "notification_service_error": ERROR_SCENARIO_NOTIFICATION_SERVICE,
    "comment_validation_error": ERROR_SCENARIO_COMMENT_VALIDATION,
}


# =============================================================================
# TEST CONFIGURATION (following existing pattern)
# =============================================================================

NOTIFY_ASSIGNEES_TEST_CONFIG = {
    "database": {
        "engine": "sqlite:///:memory:",
        "echo": False,
    },
    "email": {
        "mock_smtp": True,
        "mock_assignees": True,
        "mock_notification_service": True,
    },
    "logging": {
        "level": "INFO",
        "capture_logs": True,
    },
}


# =============================================================================
# HELPER FUNCTIONS FOR MOCK USER CREATION (following existing pattern)
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
        # Note: Intentionally no email attribute
    })()


# =============================================================================
# PARAMETRIZED TEST DATA (following existing pattern)
# =============================================================================

ERROR_SCENARIOS_PARAMETRIZED = [
    ("task_not_found", ERROR_SCENARIO_TASK_NOT_FOUND),
    ("invalid_alert_type", ERROR_SCENARIO_INVALID_ALERT_TYPE), 
    ("assignment_service_error", ERROR_SCENARIO_ASSIGNMENT_SERVICE),
    ("notification_service_error", ERROR_SCENARIO_NOTIFICATION_SERVICE),
    ("comment_validation_error", ERROR_SCENARIO_COMMENT_VALIDATION),
]

VALID_ALERT_TYPES_PARAMETRIZED = [
    (alert_type, f"Test {alert_type} message") 
    for alert_type in VALID_NON_COMMENT_ALERT_TYPES
]