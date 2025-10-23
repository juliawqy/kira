VALID_TASK_NOTIFICATION = {
    "task_id": 123,
    "task_title": "Implement User Authentication",
    "updated_fields": ["title", "priority"],
    "previous_values": {
        "title": "Add User Login",
        "priority": "Medium"
    },
    "new_values": {
        "title": "Implement User Authentication",
        "priority": "High"
    },
    "task_url": "http://localhost:8000/tasks/123"
}

MINIMAL_TASK_NOTIFICATION = {
    "task_id": 456,
    "task_title": "Bug Fix Task",
    "updated_fields": ["status"]
}

SINGLE_FIELD_UPDATE_NOTIFICATION = {
    "task_id": 789,
    "task_title": "Update Documentation",
    "updated_fields": ["description"],
    "previous_values": {
        "description": "Old documentation content"
    },
    "new_values": {
        "description": "Updated documentation with new information"
    }
}

MULTIPLE_FIELDS_UPDATE_NOTIFICATION = {
    "task_id": 999,
    "task_title": "Complete Project Setup",
    "updated_fields": ["title", "description", "priority", "start_date", "deadline"],
    "previous_values": {
        "title": "Initial Project Setup",
        "description": "Basic project initialization",
        "priority": "Low",
        "start_date": "2025-10-01",
        "deadline": "2025-10-31"
    },
    "new_values": {
        "title": "Complete Project Setup",
        "description": "Comprehensive project setup with all configurations",
        "priority": "Critical",
        "start_date": "2025-10-05",
        "deadline": "2025-10-25"
    },
    "task_url": "http://localhost:8000/tasks/999"
}


EMPTY_UPDATED_FIELDS_NOTIFICATION = {
    "task_id": 111,
    "task_title": "No Changes Task",
    "updated_fields": [],
    "previous_values": {},
    "new_values": {},
    "task_url": "http://localhost:8000/tasks/111"
}

NULL_VALUES_NOTIFICATION = {
    "task_id": 222,
    "task_title": "Null Values Task",
    "updated_fields": ["description"],
    "previous_values": None,
    "new_values": None,
    "task_url": None
}

LARGE_DATA_NOTIFICATION = {
    "task_id": 333,
    "task_title": "Large Data Task",
    "updated_fields": [f"field_{i}" for i in range(100)],
    "previous_values": {f"field_{i}": f"old_value_{i}" for i in range(100)},
    "new_values": {f"field_{i}": f"new_value_{i}" for i in range(100)},
    "task_url": "http://localhost:8000/tasks/333"
}


NOTIFY_ACTIVITY_SUCCESS_PARAMS = {
    "user_email": "u@example.com",
    "task_id": 1,
    "task_title": "T",
    "type_of_alert": "task_update",
    "updated_fields": ["title"],
    "old_values": {"title": "a"},
    "new_values": {"title": "b"},
    "to_recipients": ["r@example.com"],
}

NOTIFY_ACTIVITY_FAILURE_PARAMS = {
    "user_email": "u@example.com",
    "task_id": 2,
    "task_title": "T",
    "type_of_alert": "task_update",
    "updated_fields": ["title"],
    "old_values": {"title": "a"},
    "new_values": {"title": "b"},
    "to_recipients": ["r@example.com"],
}

NOTIFY_ACTIVITY_NO_RECIPIENTS_PARAMS = {
    "user_email": "u@example.com",
    "task_id": 3,
    "task_title": "T",
    "type_of_alert": "task_update",
    "updated_fields": ["title"],
    "old_values": {},
    "new_values": {},
    "to_recipients": [],
}

NOTIFY_ACTIVITY_INVALID_TYPE_PARAMS = {
    "user_email": "u@example.com",
    "task_id": 4,
    "task_title": "T",
    "type_of_alert": "bogus",
    "updated_fields": [],
}

NOTIFY_ACTIVITY_COMMENT_MISSING_USER_PARAMS = {
    "user_email": "u@example.com",
    "task_id": 5,
    "task_title": "T",
    "type_of_alert": "comment_create",
    "updated_fields": [],
    
}

NOTIFY_ACTIVITY_COMMENT_WITH_USER_PARAMS = {
    "user_email": "actor@example.com",
    "task_id": 6,
    "task_title": "Commented Task",
    "type_of_alert": "comment_create",
    "comment_user": "commenter@example.com",
    "updated_fields": [],
}


SUCCESSFUL_NOTIFICATION_RESPONSE = {
    "success": True,
    "message": "Notification sent successfully",
    "recipients_count": 1
}

FAILED_NOTIFICATION_RESPONSE = {
    "success": False,
    "message": "Failed to send notification",
    "recipients_count": 0
}

MULTIPLE_RECIPIENTS_NOTIFICATION_RESPONSE = {
    "success": True,
    "message": "Notification sent to multiple recipients",
    "recipients_count": 3
}


EMAIL_SERVICE_ERROR = "Email service connection failed"
SMTP_TIMEOUT_ERROR = "SMTP connection timeout"
INVALID_RECIPIENT_ERROR = "Invalid recipient email address"
TEMPLATE_RENDER_ERROR = "Template rendering failed"


NOTIFICATION_SERVICE_CONFIG = {
    "email_enabled": True,
    "sms_enabled": False,
    "push_enabled": False,
    "default_template": "task_updated"
}


TASK_TITLE_UPDATE = {
    "scenario": "title_change",
    "task_id": 501,
    "original": {"title": "Original Task Title"},
    "updated": {"title": "Updated Task Title"},
    "expected_fields": ["title"]
}

TASK_PRIORITY_UPDATE = {
    "scenario": "priority_change", 
    "task_id": 502,
    "original": {"priority": "Low"},
    "updated": {"priority": "High"},
    "expected_fields": ["priority"]
}

TASK_STATUS_UPDATE = {
    "scenario": "status_change",
    "task_id": 503,
    "original": {"status": "TODO"},
    "updated": {"status": "IN_PROGRESS"},
    "expected_fields": ["status"]
}

TASK_DATES_UPDATE = {
    "scenario": "dates_change",
    "task_id": 504,
    "original": {
        "start_date": "2025-10-01",
        "deadline": "2025-10-15"
    },
    "updated": {
        "start_date": "2025-10-05", 
        "deadline": "2025-10-20"
    },
    "expected_fields": ["start_date", "deadline"]
}

TASK_COMPLETE_UPDATE = {
    "scenario": "complete_update",
    "task_id": 505,
    "original": {
        "title": "Basic Task",
        "description": "Simple description",
        "priority": "Medium",
        "status": "TODO"
    },
    "updated": {
        "title": "Advanced Task",
        "description": "Detailed description with requirements",
        "priority": "High",
        "status": "IN_PROGRESS"
    },
    "expected_fields": ["title", "description", "priority", "status"]
}


LOG_SUCCESS_INFO = "Processing task update notification for task {task_id}"
LOG_SUCCESS_COMPLETE = "Task update notification sent successfully for task {task_id}"
LOG_EMAIL_FAILURE = "Failed to send task update notification: {error_message}"
LOG_EXCEPTION_ERROR = "Error in notify_task_updated: {exception_message}"


PERFORMANCE_TEST_NOTIFICATION = {
    "task_id": 9999,
    "task_title": "Performance Test Task",
    "updated_fields": ["title"] * 1000,  # Large number of fields
    "previous_values": {"field_" + str(i): f"old_{i}" for i in range(1000)},
    "new_values": {"field_" + str(i): f"new_{i}" for i in range(1000)}
}


NOTIFICATION_BATCH_SMALL = [
    {"task_id": 601, "task_title": "Batch Task 1", "updated_fields": ["title"]},
    {"task_id": 602, "task_title": "Batch Task 2", "updated_fields": ["priority"]},
    {"task_id": 603, "task_title": "Batch Task 3", "updated_fields": ["status"]}
]

NOTIFICATION_BATCH_LARGE = [
    {"task_id": 700 + i, "task_title": f"Batch Task {i}", "updated_fields": ["title"]}
    for i in range(50)
]


UNICODE_NOTIFICATION_DATA = {
    "task_id": 888,
    "task_title": "Tëst Tàsk with Ünicöde Chäräctërs",
    "updated_fields": ["title", "description"],
    "previous_values": {
        "title": "Öld Tïtlë",
        "description": "Prëvïöus dëscrïptïön"
    },
    "new_values": {
        "title": "Tëst Tàsk with Ünicöde Chäräctërs",
        "description": "Üpdätëd dëscrïptïön wïth spëcïäl chäräctërs"
    }
}

SPECIAL_CHARACTERS_NOTIFICATION = {
    "task_id": 777,
    "task_title": "Task with <special> & characters \"quotes\"",
    "updated_fields": ["title"],
    "previous_values": {
        "title": "Old & Previous <title>"
    },
    "new_values": {
        "title": "Task with <special> & characters \"quotes\""
    }
}


CUSTOM_EVENT_ACTIVITY_PARAMS = {
    "user_email": "actor@example.com",
    "task_id": 321,
    "task_title": "Demo Task",
    "type_of_alert": "custom_event",
    "updated_fields": [],
    "old_values": {},
    "new_values": {},
}