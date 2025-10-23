"""Centralized mock data for integration tests (email settings variants and task factory defaults)."""

EMAIL_SETTINGS_TLS = {
    "fastmail_smtp_host": "smtp.fastmail.com",
    "fastmail_smtp_port": 587,
    "fastmail_username": "ci@test.com",
    "fastmail_password": "secret",
    "fastmail_from_email": "noreply@test.com",
    "fastmail_from_name": "KIRA CI",
    "app_name": "KIRA",
    "app_url": "http://localhost:8000",
    "use_tls": True,
    "use_ssl": False,
    "timeout": 15,
}

EMAIL_SETTINGS_SSL = {
    "fastmail_smtp_host": "smtp.fastmail.com",
    "fastmail_smtp_port": 465,
    "fastmail_username": "ci@test.com",
    "fastmail_password": "secret",
    "fastmail_from_email": "noreply@test.com",
    "fastmail_from_name": "KIRA CI",
    "app_name": "KIRA",
    "app_url": "http://localhost:8000",
    "use_tls": False,
    "use_ssl": True,
    "timeout": 15,
}

EMAIL_SETTINGS_PLAIN = {
    "fastmail_smtp_host": "smtp.fastmail.com",
    "fastmail_smtp_port": 25,
    "fastmail_username": "ci@test.com",
    "fastmail_password": "secret",
    "fastmail_from_email": "noreply@test.com",
    "fastmail_from_name": "KIRA CI",
    "app_name": "KIRA",
    "app_url": "http://localhost:8000",
    "use_tls": False,
    "use_ssl": False,
    "timeout": 10,
}

# Default inputs for task_factory used in notification_and_email integration tests
TASK_FACTORY_INITIAL = {
    "title": "Initial Title",
    "project_id": 1,
}

TASK_FACTORY_OOPS = {
    "title": "Oops Title",
    "project_id": 1,
}
