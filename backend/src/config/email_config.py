"""
Email configuration settings for FastMail integration
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class EmailSettings(BaseSettings):
    """Email configuration settings"""
    
    # FastMail SMTP Configuration
    fastmail_smtp_host: str = "smtp.fastmail.com"
    fastmail_smtp_port: int = 587
    fastmail_username: str = ""
    fastmail_password: str = ""
    fastmail_from_email: str = ""
    fastmail_from_name: str = "Kira Task Management"
    
    # Application Configuration
    app_name: str = "Kira Task Management System"
    app_url: str = "http://localhost:8000"
    
    # Email Settings
    use_tls: bool = True
    use_ssl: bool = False
    timeout: int = 60

    # Test/Dev convenience: force notification recipient for local runs
    # Set via env TEST_RECIPIENT_EMAIL / TEST_RECIPIENT_NAME
    test_recipient_email: Optional[str] = None
    test_recipient_name: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_email_settings() -> EmailSettings:
    """Create a fresh EmailSettings instance (reads current env)."""
    return EmailSettings()