"""Mock data for integration tests between notification and email services"""

# Task update integration scenarios
INTEGRATION_SINGLE_TITLE_UPDATE = {
    "original_task": {
        "id": 1001,
        "title": "Original Task Title",
        "description": "Test task for integration",
        "priority": 3,
        "project_id": 1,
        "start_date": None,
        "deadline": None
    },
    "update_data": {
        "title": "Updated Task Title for Integration Test"
    },
    "expected_notification": {
        "task_id": 1001,
        "task_title": "Updated Task Title for Integration Test",
        "updated_fields": ["title"],
        "previous_values": {"title": "Original Task Title"},
        "new_values": {"title": "Updated Task Title for Integration Test"}
    }
}

INTEGRATION_MULTIPLE_DATES_UPDATE = {
    "original_task": {
        "id": 1002,
        "title": "Date Update Integration Test",
        "description": "Test task for date updates",
        "priority": 2,
        "project_id": 1,
        "start_date": "2025-10-01",
        "deadline": "2025-10-31"
    },
    "update_data": {
        "start_date": "2025-10-15",
        "deadline": "2025-11-15"
    },
    "expected_notification": {
        "task_id": 1002,
        "task_title": "Date Update Integration Test",
        "updated_fields": ["start_date", "deadline"],
        "previous_values": {
            "start_date": "2025-10-01",
            "deadline": "2025-10-31"
        },
        "new_values": {
            "start_date": "2025-10-15",
            "deadline": "2025-11-15"
        }
    }
}

INTEGRATION_COMPLETE_UPDATE = {
    "original_task": {
        "id": 1003,
        "title": "Complete Integration Test Task",
        "description": "Original description",
        "priority": 1,
        "project_id": 1,
        "start_date": "2025-10-01",
        "deadline": "2025-10-15"
    },
    "update_data": {
        "title": "Updated Complete Integration Test",
        "description": "Updated description with more details",
        "priority": 5,
        "start_date": "2025-10-05",
        "deadline": "2025-10-25"
    },
    "expected_notification": {
        "task_id": 1003,
        "task_title": "Updated Complete Integration Test",
        "updated_fields": ["title", "description", "priority", "start_date", "deadline"],
        "previous_values": {
            "title": "Complete Integration Test Task",
            "description": "Original description",
            "priority": 1,
            "start_date": "2025-10-01",
            "deadline": "2025-10-15"
        },
        "new_values": {
            "title": "Updated Complete Integration Test",
            "description": "Updated description with more details",
            "priority": 5,
            "start_date": "2025-10-05",
            "deadline": "2025-10-25"
        }
    }
}

INTEGRATION_NO_CHANGES = {
    "original_task": {
        "id": 1004,
        "title": "No Changes Task",
        "description": "This task won't change",
        "priority": 3,
        "project_id": 1,
        "start_date": None,
        "deadline": None
    },
    "update_data": {
        "title": "No Changes Task",  # Same as original
        "priority": 3  # Same as original
    },
    "expected_notification": None  # No notification should be sent
}

# Email service integration scenarios
EMAIL_SERVICE_SUCCESS_SCENARIO = {
    "recipients": [
        {"email": "integration@test.com", "name": "Integration Tester"}
    ],
    "response": {
        "success": True,
        "message": "Integration test email sent successfully",
        "recipients_count": 1
    }
}

EMAIL_SERVICE_FAILURE_SCENARIO = {
    "recipients": [],  # No recipients
    "response": {
        "success": True,
        "message": "No recipients configured for notifications", 
        "recipients_count": 0
    }
}

EMAIL_SERVICE_ERROR_SCENARIO = {
    "recipients": [
        {"email": "error@test.com", "name": "Error Tester"}
    ],
    "error": "SMTP connection failed",
    "response": {
        "success": False,
        "message": "SMTP connection failed",
        "recipients_count": 0
    }
}

# Full pipeline test scenarios
PIPELINE_SUCCESS_SCENARIO = {
    "task_update": INTEGRATION_SINGLE_TITLE_UPDATE,
    "notification_success": True,
    "email_success": True,
    "expected_result": "Task updated and notification sent successfully"
}

PIPELINE_NOTIFICATION_FAILURE = {
    "task_update": INTEGRATION_MULTIPLE_DATES_UPDATE,
    "notification_success": False,
    "notification_error": "Notification service connection failed",
    "expected_result": "Task updated but notification failed"
}

PIPELINE_EMAIL_FAILURE = {
    "task_update": INTEGRATION_COMPLETE_UPDATE,
    "notification_success": True,
    "email_success": False,
    "email_error": "Email service unavailable",
    "expected_result": "Task updated but email sending failed"
}

# Service communication test data
SERVICE_COMMUNICATION_SUCCESS = {
    "notification_to_email_call": {
        "task_id": 2001,
        "task_title": "Service Communication Test",
        "updated_fields": ["priority"],
        "previous_values": {"priority": "Low"},
        "new_values": {"priority": "High"}
    },
    "email_service_response": {
        "success": True,
        "message": "Email sent via service communication",
        "recipients_count": 2
    }
}

SERVICE_COMMUNICATION_FAILURE = {
    "notification_to_email_call": {
        "task_id": 2002,
        "task_title": "Service Communication Failure Test", 
        "updated_fields": ["status"],
        "previous_values": {"status": "TODO"},
        "new_values": {"status": "DONE"}
    },
    "email_service_error": "Service communication timeout",
    "expected_error_response": {
        "success": False,
        "message": "Notification service error: Service communication timeout",
        "recipients_count": 0
    }
}

# Error handling integration scenarios
ERROR_HANDLING_TASK_UPDATE_CONTINUES = {
    "task_data": {
        "id": 3001,
        "title": "Error Handling Test",
        "description": "Test resilience to notification failures"
    },
    "update_data": {
        "description": "Updated despite notification failure"
    },
    "notification_error": "Email system down",
    "expected_outcome": "Task update succeeds despite notification failure"
}

ERROR_HANDLING_LOGGING_TEST = {
    "task_id": 3002,
    "notification_error": "Test logging error for integration",
    "expected_logs": [
        "Processing task update notification for task 3002",
        "Error in notify_task_updated: Test logging error for integration"
    ]
}

# Recipient determination test scenarios
RECIPIENT_DETERMINATION_WITH_RECIPIENTS = {
    "task_id": 4001,
    "mock_recipients": [
        {"email": "user1@example.com", "name": "User One"},
        {"email": "user2@example.com", "name": "User Two"}
    ],
    "expected_email_call": True,
    "expected_recipients_count": 2
}

RECIPIENT_DETERMINATION_NO_RECIPIENTS = {
    "task_id": 4002,
    "mock_recipients": [],
    "expected_email_call": False,
    "expected_response": {
        "success": True,
        "message": "No recipients configured for notifications",
        "recipients_count": 0
    }
}

# Performance integration test data
PERFORMANCE_INTEGRATION_TEST = {
    "task_data": {
        "id": 5001,
        "title": "Performance Integration Test"
    },
    "large_update_data": {
        f"field_{i}": f"value_{i}" for i in range(50)
    },
    "expected_notification_fields": [f"field_{i}" for i in range(50)],
    "performance_threshold_ms": 1000  # Max 1 second for processing
}

# Mock database session scenarios
MOCK_SESSION_SUCCESS = {
    "session_type": "successful_transaction",
    "operations": ["get", "add", "flush"],
    "expected_calls": 3
}

MOCK_SESSION_ROLLBACK = {
    "session_type": "rollback_on_error",
    "error_at_step": "flush",
    "error_type": "DatabaseError",
    "expected_rollback": True
}

# Integration test validation data
INTEGRATION_VALIDATION_CHECKLIST = {
    "task_update": [
        "Task retrieved from database",
        "Fields updated correctly", 
        "Changes persisted to database"
    ],
    "notification_trigger": [
        "Notification service called",
        "Correct parameters passed",
        "Updated fields identified"
    ],
    "email_sending": [
        "Email service invoked",
        "Recipients determined",
        "Email content prepared",
        "SMTP connection attempted"
    ],
    "error_handling": [
        "Exceptions caught gracefully",
        "Appropriate logs generated",
        "Task update not rolled back"
    ]
}

# Test environment configuration
INTEGRATION_TEST_CONFIG = {
    "database": {
        "engine": "sqlite:///:memory:",
        "echo": False
    },
    "email": {
        "mock_smtp": True,
        "mock_recipients": True
    },
    "logging": {
        "level": "DEBUG",
        "capture_logs": True
    }
}