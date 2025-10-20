"""Mock data for email templates tests"""

# Basic template rendering data
BASIC_TEMPLATE_DATA = {
    "app_name": "KIRA",
    "assignee_name": "John Doe",
    "task_title": "Complete Project Documentation",
    "task_id": 123,
    "updated_by": "Jane Smith",
    "update_date": "2025-10-15",
    "updated_fields": ["title", "priority"],
    "previous_values": {
        "title": "Project Documentation",
        "priority": "Medium"
    },
    "new_values": {
        "title": "Complete Project Documentation", 
        "priority": "High"
    },
    "task_url": "http://localhost:8000/tasks/123"
}

MINIMAL_TEMPLATE_DATA = {
    "app_name": "KIRA",
    "task_title": "Simple Task",
    "task_id": 456,
    "updated_by": "System",
    "update_date": "2025-10-15",
    "updated_fields": ["status"],
    "assignee_name": "Test User"
}

COMPLETE_TEMPLATE_DATA = {
    "app_name": "KIRA Project Management System",
    "assignee_name": "Alice Johnson",
    "task_title": "Implement Advanced Authentication System",
    "task_id": 789,
    "updated_by": "Bob Manager",
    "update_date": "2025-10-15 14:30:00",
    "updated_fields": ["title", "description", "priority", "start_date", "deadline"],
    "previous_values": {
        "title": "Basic Authentication",
        "description": "Simple login system",
        "priority": "Low",
        "start_date": "2025-10-01",
        "deadline": "2025-11-01"
    },
    "new_values": {
        "title": "Implement Advanced Authentication System",
        "description": "Multi-factor authentication with OAuth2 integration",
        "priority": "Critical",
        "start_date": "2025-10-05",
        "deadline": "2025-10-25"
    },
    "task_url": "https://kira.example.com/tasks/789"
}

# Edge case template data
NULL_ASSIGNEE_TEMPLATE_DATA = {
    "app_name": "KIRA",
    "assignee_name": None,  # Should fallback to "Team Member"
    "task_title": "Task with No Assignee",
    "task_id": 999,
    "updated_by": "Admin",
    "update_date": "2025-10-15",
    "updated_fields": ["status"],
    "previous_values": {"status": "TODO"},
    "new_values": {"status": "IN_PROGRESS"}
}

EMPTY_FIELDS_TEMPLATE_DATA = {
    "app_name": "KIRA",
    "assignee_name": "Test User",
    "task_title": "No Changes Task",
    "task_id": 111,
    "updated_by": "System",
    "update_date": "2025-10-15",
    "updated_fields": [],  # Empty fields list
    "previous_values": {},
    "new_values": {}
}

MISSING_VALUES_TEMPLATE_DATA = {
    "app_name": "KIRA",
    "assignee_name": "Test User",
    "task_title": "Missing Values Task",
    "task_id": 222,
    "updated_by": None,
    "update_date": "2025-10-15",
    "updated_fields": ["title"],
    "previous_values": None,
    "new_values": None,
    "task_url": None
}

# Special characters and unicode data
UNICODE_TEMPLATE_DATA = {
    "app_name": "KIRA™",
    "assignee_name": "José María García",
    "task_title": "Tëst Tàsk with Ünicöde Chäräctërs",
    "task_id": 333,
    "updated_by": "Administrador & Manager",
    "update_date": "2025-10-15",
    "updated_fields": ["title", "description"],
    "previous_values": {
        "title": "Tàskà Prëvïöüs",
        "description": "Dëscrípcíón con caräctëres especíales"
    },
    "new_values": {
        "title": "Tëst Tàsk with Ünicöde Chäräctërs",
        "description": "Üpdätëd dëscrípcíón wíth mörë spëcíäl chäräctërs"
    }
}

SPECIAL_CHARS_TEMPLATE_DATA = {
    "app_name": "KIRA <System>",
    "assignee_name": "User & Developer",
    "task_title": "Task with <HTML> & \"Special\" Characters",
    "task_id": 444,
    "updated_by": "Admin & Manager",
    "update_date": "2025-10-15",
    "updated_fields": ["title"],
    "previous_values": {
        "title": "Old <Title> & Previous"
    },
    "new_values": {
        "title": "Task with <HTML> & \"Special\" Characters"
    }
}

# Long content test data
LONG_CONTENT_TEMPLATE_DATA = {
    "app_name": "KIRA",
    "assignee_name": "Test User with Very Long Name for Testing Purposes",
    "task_title": "A" * 200,  # Very long title (200 characters)
    "task_id": 555,
    "updated_by": "System Administrator with Long Title",
    "update_date": "2025-10-15",
    "updated_fields": ["title", "description"],
    "previous_values": {
        "title": "Short Title",
        "description": "Short description"
    },
    "new_values": {
        "title": "A" * 200,
        "description": "B" * 1000  # Very long description (1000 characters)
    },
    "task_url": "https://very-long-domain-name-for-testing.example.com/tasks/555"
}

# Multiple field changes scenarios
SINGLE_FIELD_CHANGE_DATA = {
    "app_name": "KIRA",
    "assignee_name": "Developer",
    "task_title": "Single Field Update",
    "task_id": 601,
    "updated_by": "Manager",
    "update_date": "2025-10-15",
    "updated_fields": ["priority"],
    "previous_values": {"priority": "Low"},
    "new_values": {"priority": "Critical"}
}

MULTIPLE_FIELD_CHANGES_DATA = {
    "app_name": "KIRA",
    "assignee_name": "Senior Developer",
    "task_title": "Multi-Field Update Task",
    "task_id": 602,
    "updated_by": "Project Manager",
    "update_date": "2025-10-15",
    "updated_fields": ["title", "description", "priority", "deadline", "status"],
    "previous_values": {
        "title": "Original Task",
        "description": "Basic task description",
        "priority": "Medium",
        "deadline": "2025-11-01",
        "status": "TODO"
    },
    "new_values": {
        "title": "Multi-Field Update Task",
        "description": "Comprehensive task description with detailed requirements",
        "priority": "High",
        "deadline": "2025-10-20",
        "status": "IN_PROGRESS"
    }
}

MANY_FIELDS_CHANGES_DATA = {
    "app_name": "KIRA",
    "assignee_name": "Lead Developer",
    "task_title": "Task with Many Field Updates",
    "task_id": 603,
    "updated_by": "System",
    "update_date": "2025-10-15",
    "updated_fields": [f"field_{i}" for i in range(20)],  # 20 different fields
    "previous_values": {f"field_{i}": f"old_value_{i}" for i in range(20)},
    "new_values": {f"field_{i}": f"new_value_{i}" for i in range(20)}
}

# Template structure validation data
EXPECTED_HTML_ELEMENTS = [
    "<!DOCTYPE html>",
    "<html>",
    "<head>",
    "<body>",
    "<title>",
    "</html>"
]

EXPECTED_JINJA_VARIABLES = [
    "{{ app_name }}",
    "{{ assignee_name",
    "{{ task_title }}",
    "{{ task_id }}",
    "{{ updated_by }}",
    "{{ update_date }}",
    "{{ updated_fields }}"
]

EXPECTED_CSS_CLASSES = [
    "container",
    "header",
    "content",
    "task-info",
    "changes",
    "footer"
]

# Performance test data for templates
PERFORMANCE_TEMPLATE_DATA = {
    "app_name": "KIRA Performance Test",
    "assignee_name": "Performance Tester",
    "task_title": "Performance Test Task with Large Data Set",
    "task_id": 9999,
    "updated_by": "Performance System",
    "update_date": "2025-10-15",
    "updated_fields": [f"performance_field_{i}" for i in range(100)],
    "previous_values": {f"performance_field_{i}": f"old_perf_value_{i}" * 10 for i in range(100)},
    "new_values": {f"performance_field_{i}": f"new_perf_value_{i}" * 10 for i in range(100)}
}

# Template rendering result validation
EXPECTED_RENDERED_CONTENT = {
    "should_contain": [
        "KIRA",
        "Task Update Notification", 
        "has been updated",
        "Updated by:",
        "Task ID:"
    ],
    "should_not_contain": [
        "{{",  # No unrendered template variables
        "}}",
        "None",  # No Python None values
        "undefined"  # No Jinja2 undefined values
    ]
}

# Different template scenarios
TEMPLATE_SCENARIOS = {
    "basic_update": BASIC_TEMPLATE_DATA,
    "minimal_data": MINIMAL_TEMPLATE_DATA,
    "complete_data": COMPLETE_TEMPLATE_DATA,
    "null_assignee": NULL_ASSIGNEE_TEMPLATE_DATA,
    "empty_fields": EMPTY_FIELDS_TEMPLATE_DATA,
    "unicode_content": UNICODE_TEMPLATE_DATA,
    "special_chars": SPECIAL_CHARS_TEMPLATE_DATA,
    "long_content": LONG_CONTENT_TEMPLATE_DATA,
    "single_field": SINGLE_FIELD_CHANGE_DATA,
    "multiple_fields": MULTIPLE_FIELD_CHANGES_DATA,
    "performance_test": PERFORMANCE_TEMPLATE_DATA
}

# Template validation patterns
HTML_VALIDATION_PATTERNS = [
    r"<html[^>]*>.*</html>",
    r"<head>.*</head>", 
    r"<body>.*</body>",
    r"<title>.*</title>"
]

JINJA_VARIABLE_PATTERNS = [
    r"\{\{\s*\w+\s*\}\}",  # Basic variables
    r"\{\{\s*\w+\s*\|\s*\w+\s*\}\}",  # Variables with filters
    r"\{\%.*?\%\}"  # Jinja2 statements
]