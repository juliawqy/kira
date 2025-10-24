RENDER_DATA_BASIC = {
    'app_name': 'KIRA',
    'assignee_name': 'John Doe',
    'task_title': 'Complete Project Documentation',
    'task_id': 123,
    'updated_by': 'Jane Smith',
    'update_date': '2025-10-15',
    'updated_fields': ['title', 'priority'],
    'previous_values': {'title': 'Old Title', 'priority': 'LOW'},
    'new_values': {'title': 'New Title', 'priority': 'HIGH'},
    'task_url': 'http://localhost:8000/tasks/123',
}


RENDER_DATA_MISSING_ASSIGNEE = {
    'app_name': 'KIRA',
    'assignee_name': None,
    'task_title': 'Test Task',
    'task_id': 456,
    'updated_by': 'System',
    'update_date': '2025-10-15',
    'updated_fields': ['status'],
    'previous_values': {'status': 'TODO'},
    'new_values': {'status': 'IN_PROGRESS'},
}

RENDER_DATA_EMPTY_FIELDS = {
    'app_name': 'KIRA',
    'assignee_name': 'Test User',
    'task_title': 'Test Task',
    'task_id': 789,
    'updated_by': 'Admin',
    'update_date': '2025-10-15',
    'updated_fields': [],
    'previous_values': {},
    'new_values': {},
}


RENDER_DATA_MULTIPLE_CHANGES = {
    'app_name': 'KIRA',
    'assignee_name': 'Test User',
    'task_title': 'Multi-Update Task',
    'task_id': 999,
    'updated_by': 'Project Manager',
    'update_date': '2025-10-15',
    'updated_fields': ['title', 'description', 'priority', 'deadline'],
    'previous_values': {
        'title': 'Old Title',
        'description': 'Old Description',
        'priority': 'LOW',
        'deadline': '2025-10-01',
    },
    'new_values': {
        'title': 'New Title',
        'description': 'New Description',
        'priority': 'HIGH',
        'deadline': '2025-10-31',
    },
}

# Special characters
RENDER_DATA_SPECIAL_CHARS = {
    'app_name': 'KIRA™',
    'assignee_name': 'José María',
    'task_title': 'Task with <special> & characters',
    'task_id': 101,
    'updated_by': 'Admin & Manager',
    'update_date': '2025-10-15',
    'updated_fields': ['title'],
    'previous_values': {'title': 'Old & Previous'},
    'new_values': {'title': 'New & Updated'},
}

# Very long content
_LONG_TITLE = 'A' * 200
_LONG_DESCRIPTION = 'B' * 1000
RENDER_DATA_LONG_CONTENT = {
    'app_name': 'KIRA',
    'assignee_name': 'Test User',
    'task_title': _LONG_TITLE,
    'task_id': 202,
    'updated_by': 'System',
    'update_date': '2025-10-15',
    'updated_fields': ['title', 'description'],
    'previous_values': {'title': 'Short', 'description': 'Short desc'},
    'new_values': {'title': _LONG_TITLE, 'description': _LONG_DESCRIPTION},
}

# None values
RENDER_DATA_NONE_VALUES = {
    'app_name': 'KIRA',
    'assignee_name': None,
    'task_title': 'Test Task',
    'task_id': 303,
    'updated_by': None,
    'update_date': '2025-10-15',
    'updated_fields': ['status'],
    'previous_values': None,
    'new_values': None,
    'task_url': None,
}

# Numeric and boolean values
RENDER_DATA_NUMERIC_BOOLEAN = {
    'app_name': 'KIRA',
    'assignee_name': 'Test User',
    'task_title': 'Numeric Test Task',
    'task_id': 404,
    'updated_by': 'System',
    'update_date': '2025-10-15',
    'updated_fields': ['priority', 'active'],
    'previous_values': {'priority': 3, 'active': True},
    'new_values': {'priority': 5, 'active': False},
}

# Performance data
RENDER_DATA_PERFORMANCE = {
    'app_name': 'KIRA',
    'assignee_name': 'Performance Test User',
    'task_title': 'Performance Test Task',
    'task_id': 505,
    'updated_by': 'Test System',
    'update_date': '2025-10-15',
    'updated_fields': [f"field_{i}" for i in range(50)],
    'previous_values': {f"field_{i}": f"old_value_{i}" for i in range(50)},
    'new_values': {f"field_{i}": f"new_value_{i}" for i in range(50)},
}
