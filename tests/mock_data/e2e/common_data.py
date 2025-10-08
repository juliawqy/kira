"""
General E2E test data that applies across modules.
Contains shared UI patterns, navigation data, and cross-module scenarios.
"""

# Common E2E UI Patterns
COMMON_UI_PATTERNS = {
    "buttons": {
        "submit": "button[type='submit']",
        "cancel": ".btn-cancel",
        "delete": ".btn-delete",
        "update": ".btn-update",
        "save": ".btn-save",
        "refresh": "#refresh"
    },
    "forms": {
        "required_field_error": "This field is required",
        "validation_error_class": ".error",
        "success_class": ".success"
    },
    "navigation": {
        "back_button_pattern": "//button[contains(text(), '← Back')]",
        "breadcrumb_separator": " > "
    }
}

# Common E2E Wait Times (in seconds)
E2E_TIMEOUTS = {
    "short_wait": 1,
    "medium_wait": 2,
    "long_wait": 5,
    "api_response": 3,
    "page_load": 10
}

# Common E2E Status Messages
STATUS_MESSAGES = {
    "success_indicators": ["successfully", "completed", "saved"],
    "error_indicators": ["error", "failed", "invalid"],
    "loading_indicators": ["loading", "processing", "please wait"]
}

# Cross-module test scenarios
CROSS_MODULE_SCENARIOS = {
    "user_task_workflow": {
        "description": "Create user, then create task assigned to that user",
        "steps": ["create_user", "create_task", "assign_task", "verify_assignment"]
    },
    "bulk_operations": {
        "description": "Test bulk operations across modules",
        "batch_size": 10,
        "timeout_multiplier": 2
    }
}
