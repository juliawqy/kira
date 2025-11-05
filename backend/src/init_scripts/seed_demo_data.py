from datetime import date, datetime, timedelta
from backend.src.database.db_setup import SessionLocal
from backend.src.handlers import user_handler, task_handler, task_assignment_handler, comment_handler, department_handler, project_handler, report_handler
from backend.src.enums.user_role import UserRole
from backend.src.enums.task_status import TaskStatus
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def seed_database():
    """Seed the database with demo data."""

    # Create Root Admin User
    admin_user = {
        "name": "Admin",
        "email": "admin@example.com",
        "password": "Admin123!",
        "role": UserRole.HR,
        "admin": True,
    }

    user_handler.create_user(**admin_user)

    # Create Departments
    departments = [
        {"name": "Engineering", "description": "Handles all engineering tasks."},
        {"name": "Marketing", "description": "Responsible for marketing and outreach."},
        {"name": "Sales", "description": "Manages client relationships and sales."},
    ]


if __name__ == "__main__":
    seed_database()