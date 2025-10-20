"""Mock data for email service tests"""

# Valid email settings configurations
VALID_EMAIL_SETTINGS = {
    "smtp_server": "smtp.fastmail.com",
    "smtp_port": 587,
    "username": "test@fastmail.com",
    "password": "test_password",
    "from_name": "KIRA Test App",
    "app_url": "http://localhost:8000"
}

ALTERNATIVE_EMAIL_SETTINGS = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 465,
    "username": "kira@gmail.com",
    "password": "secure_password",
    "from_name": "KIRA Project Manager",
    "app_url": "https://kira.example.com"
}

# Invalid email settings for testing validation
INVALID_EMAIL_SETTINGS_EMPTY = {
    "smtp_server": "",
    "smtp_port": 587,
    "username": "",
    "password": "",
    "from_name": "",
    "app_url": ""
}

INVALID_EMAIL_SETTINGS_MISSING_PORT = {
    "smtp_server": "smtp.test.com",
    "smtp_port": None,
    "username": "test@test.com",
    "password": "password",
    "from_name": "Test App",
    "app_url": "http://test.com"
}

# Sample email recipients
VALID_EMAIL_RECIPIENTS = [
    {
        "email": "john.doe@fastmail.com",
        "name": "John Doe"
    },
    {
        "email": "jane.smith@fastmail.com",
        "name": "Jane Smith"
    },
    {
        "email": "admin@fastmail.com",
        "name": "Admin User"
    }
]

SINGLE_EMAIL_RECIPIENT = [
    {
        "email": "user@fastmail.com",
        "name": "Test User"
    }
]

EMAIL_RECIPIENTS_NO_NAMES = [
    {
        "email": "user1@fastmail.com",
        "name": None
    },
    {
        "email": "user2@fastmail.com", 
        "name": None
    }
]

# Sample email content
VALID_EMAIL_CONTENT_HTML_TEXT = {
    "subject": "Task Update Notification",
    "html_body": "<p>Your task has been updated.</p>",
    "text_body": "Your task has been updated."
}

VALID_EMAIL_CONTENT_TEMPLATE = {
    "subject": "Task Updated: Complete Project Documentation",
    "template_name": "task_updated",
    "template_data": {
        "task_id": 123,
        "task_title": "Complete Project Documentation",
        "updated_by": "John Manager",
        "updated_fields": ["title", "priority"],
        "assignee_name": "Jane Developer",
        "previous_values": {
            "title": "Old Project Documentation",
            "priority": "Low"
        },
        "new_values": {
            "title": "Complete Project Documentation",
            "priority": "High"
        }
    }
}

# Sample complete email messages
VALID_EMAIL_MESSAGE_SIMPLE = {
    "recipients": SINGLE_EMAIL_RECIPIENT,
    "content": VALID_EMAIL_CONTENT_HTML_TEXT,
    "email_type": "general_notification"
}

VALID_EMAIL_MESSAGE_TASK_UPDATE = {
    "recipients": VALID_EMAIL_RECIPIENTS,
    "content": VALID_EMAIL_CONTENT_TEMPLATE,
    "email_type": "task_updated",
    "priority": "high"
}

VALID_EMAIL_MESSAGE_WITH_CC_BCC = {
    "recipients": SINGLE_EMAIL_RECIPIENT,
    "content": VALID_EMAIL_CONTENT_HTML_TEXT,
    "cc": [{"email": "cc@example.com", "name": "CC User"}],
    "bcc": [{"email": "bcc@example.com", "name": "BCC User"}],
    "email_type": "general_notification"
}

# Task update notification data
VALID_TASK_UPDATE_NOTIFICATION = {
    "task_id": 456,
    "task_title": "Fix Authentication Bug",
    "updated_fields": ["status", "priority"],
    "previous_values": {
        "status": "TODO",
        "priority": "Medium"
    },
    "new_values": {
        "status": "IN_PROGRESS", 
        "priority": "High"
    },
    "task_url": "http://localhost:8000/tasks/456"
}

MINIMAL_TASK_UPDATE_NOTIFICATION = {
    "task_id": 789,
    "task_title": "Simple Task Update",
    "updated_fields": ["title"]
}

COMPLEX_TASK_UPDATE_NOTIFICATION = {
    "task_id": 999,
    "task_title": "Complex Multi-Field Update",
    "updated_fields": ["title", "description", "priority", "start_date", "deadline"],
    "previous_values": {
        "title": "Old Complex Task",
        "description": "Old description here",
        "priority": "Low",
        "start_date": "2025-10-01",
        "deadline": "2025-10-15"
    },
    "new_values": {
        "title": "Complex Multi-Field Update",
        "description": "Updated description with more details",
        "priority": "Critical",
        "start_date": "2025-10-05",
        "deadline": "2025-10-20"
    },
    "task_url": "http://localhost:8000/tasks/999"
}

# Email response test data
SUCCESSFUL_EMAIL_RESPONSE = {
    "success": True,
    "message": "Email sent successfully",
    "recipients_count": 1
}

FAILED_EMAIL_RESPONSE = {
    "success": False,
    "message": "SMTP server connection failed",
    "recipients_count": 0
}

MULTIPLE_RECIPIENTS_EMAIL_RESPONSE = {
    "success": True,
    "message": "Email sent to multiple recipients",
    "recipients_count": 3
}

# SMTP test scenarios
SMTP_CONNECTION_ERROR = "Connection to SMTP server failed"
SMTP_AUTH_ERROR = "SMTP authentication failed"
SMTP_SEND_ERROR = "Failed to send message via SMTP"

# Environment variable test data
ENV_VARS_COMPLETE = {
    'EMAIL_SMTP_SERVER': 'smtp.testmail.com',
    'EMAIL_SMTP_PORT': '587',
    'EMAIL_USERNAME': 'test@testmail.com',
    'EMAIL_PASSWORD': 'test_password',
    'EMAIL_FROM_NAME': 'Test KIRA App',
    'APP_URL': 'http://localhost:3000'
}

ENV_VARS_EMPTY = {
    'EMAIL_SMTP_SERVER': '',
    'EMAIL_SMTP_PORT': '587',
    'EMAIL_USERNAME': '',
    'EMAIL_PASSWORD': '',
    'EMAIL_FROM_NAME': '',
    'APP_URL': ''
}

ENV_VARS_INVALID_PORT = {
    'EMAIL_SMTP_SERVER': 'smtp.test.com',
    'EMAIL_SMTP_PORT': 'invalid_port',
    'EMAIL_USERNAME': 'user@test.com',
    'EMAIL_PASSWORD': 'password',
    'EMAIL_FROM_NAME': 'Test App',
    'APP_URL': 'http://test.com'
}

# Special character test data
UNICODE_EMAIL_DATA = {
    "recipients": [{"email": "üser@tést.com", "name": "José María"}],
    "subject": "Tëst Sübjëct with Ünicöde",
    "content": "Tëst cöntënt with spëciàl chäräctërs"
}

LONG_EMAIL_DATA = {
    "recipients": [{"email": "very.long.email.address@verylongdomainname.com", "name": "Very Long Name For Testing"}],
    "subject": "A" * 200,  # Very long subject
    "content": "B" * 1000   # Very long content
}