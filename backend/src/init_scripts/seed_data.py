"""
Seed script to populate database with initial test data.
Run this script to set up:
- Users (Cong, Julia, Manager, Director)
- Projects
- Tasks assigned to users
- Comments on tasks
"""

from datetime import date, datetime, timedelta
from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.user import User
from backend.src.database.models.task import Task
from backend.src.database.models.task_assignment import TaskAssignment
from backend.src.database.models.comment import Comment
from backend.src.database.models.project import Project
from backend.src.database.models.parent_assignment import ParentAssignment
from backend.src.enums.user_role import UserRole
from backend.src.enums.task_status import TaskStatus
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def _hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def seed_database():
    """Seed the database with initial test data."""
    session = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = session.query(User).count()
        if existing_users > 0:
            print("Database already has data. Skipping seed.")
            return
        
        print("Starting database seed...")
        
        # Create users
        print("Creating users...")
        users = {
            "cong": User(
                name="Cong",
                email="Cong@example.com",
                role=UserRole.STAFF.value,
                hashed_pw=_hash_password("Password123!"),
                admin=False
            ),
            "julia": User(
                name="Julia",
                email="Julia@example.com",
                role=UserRole.STAFF.value,
                hashed_pw=_hash_password("Password123!"),
                admin=False
            ),
            "manager": User(
                name="Manager1",
                email="manager@example.com",
                role=UserRole.MANAGER.value,
                hashed_pw=_hash_password("Password123!"),
                admin=True
            ),
            "director": User(
                name="Director1",
                email="director@example.com",
                role=UserRole.DIRECTOR.value,
                hashed_pw=_hash_password("Password123!"),
                admin=True
            )
        }
        
        session.add_all(users.values())
        session.flush()
        
        # Get user IDs after flush
        cong_id = users["cong"].user_id
        julia_id = users["julia"].user_id
        manager_id = users["manager"].user_id
        director_id = users["director"].user_id
        
        print(f"Created users: Cong (ID: {cong_id}), Julia (ID: {julia_id})")
        print(f"Created users: Manager (ID: {manager_id}), Director (ID: {director_id})")
        
        # Create projects
        print("Creating projects...")
        projects = [
            Project(
                project_id=1,
                project_name="Project Alpha",
                project_manager=manager_id,
                active=True
            ),
            Project(
                project_id=2,
                project_name="Project Beta",
                project_manager=director_id,
                active=True
            ),
            Project(
                project_id=3,
                project_name="Project Gamma",
                project_manager=manager_id,
                active=True
            )
        ]
        
        session.add_all(projects)
        session.flush()
        print(f"Created {len(projects)} projects")
        
        # Create tasks
        print("Creating tasks...")
        today = date.today()
        
        tasks = [
            # Cong's tasks
            Task(
                id=1,
                title="Moving tables",
                description="Move chairs then tables\nhello world",
                start_date=today,
                deadline=today + timedelta(days=2),
                status=TaskStatus.TO_DO.value,
                priority=7,
                recurring=0,
                tag="logistics",
                project_id=1,
                active=True
            ),
            Task(
                id=4,
                title="Update documentation",
                description="Review and update project documentation",
                start_date=today,
                deadline=today + timedelta(days=3),
                status=TaskStatus.IN_PROGRESS.value,
                priority=5,
                recurring=0,
                tag="documentation",
                project_id=1,
                active=True
            ),
            
            # Julia's tasks
            Task(
                id=2,
                title="Testing task",
                description="This is a testing task",
                start_date=today + timedelta(days=1),
                deadline=today + timedelta(days=4),
                status=TaskStatus.TO_DO.value,
                priority=8,
                recurring=3,  # Recurring every 3 days
                tag="testing",
                project_id=2,
                active=True
            ),
            Task(
                id=3,
                title="Code review",
                description="Review pull requests and provide feedback",
                start_date=today + timedelta(days=2),
                deadline=today + timedelta(days=5),
                status=TaskStatus.BLOCKED.value,
                priority=9,
                recurring=0,
                tag="development",
                project_id=2,
                active=True
            ),
            
            # Shared task
            Task(
                id=5,
                title="Team meeting preparation",
                description="Prepare agenda and materials for team meeting",
                start_date=None,
                deadline=None,
                status=TaskStatus.TO_DO.value,
                priority=6,
                recurring=0,
                tag="meeting",
                project_id=1,
                active=True
            ),
            
            # Completed task
            Task(
                id=6,
                title="Completed task",
                description="This task is already completed",
                start_date=today - timedelta(days=5),
                deadline=today - timedelta(days=2),
                status=TaskStatus.COMPLETED.value,
                priority=4,
                recurring=0,
                tag="completed",
                project_id=1,
                active=True
            ),
            
            # Project Beta additional tasks
            Task(
                id=12,
                title="Bug investigation",
                description="Debug and identify root causes of reported issues",
                start_date=today,
                deadline=today + timedelta(days=5),
                status=TaskStatus.IN_PROGRESS.value,
                priority=7,
                recurring=0,
                tag="bugfix",
                project_id=2,
                active=True
            ),
            Task(
                id=13,
                title="API documentation",
                description="Write comprehensive API documentation and examples",
                start_date=today + timedelta(days=2),
                deadline=today + timedelta(days=10),
                status=TaskStatus.TO_DO.value,
                priority=6,
                recurring=0,
                tag="documentation",
                project_id=2,
                active=True
            ),
            
            # Project Gamma tasks
            Task(
                id=11,
                title="Design new feature",
                description="Create mockups and design specifications",
                start_date=today + timedelta(days=1),
                deadline=today + timedelta(days=7),
                status=TaskStatus.TO_DO.value,
                priority=8,
                recurring=0,
                tag="design",
                project_id=3,
                active=True
            ),
            Task(
                id=14,
                title="User research interview",
                description="Conduct user interviews to gather feedback",
                start_date=today + timedelta(days=3),
                deadline=today + timedelta(days=8),
                status=TaskStatus.TO_DO.value,
                priority=7,
                recurring=0,
                tag="research",
                project_id=3,
                active=True
            ),
            Task(
                id=15,
                title="Accessibility audit",
                description="Review and improve accessibility compliance",
                start_date=today + timedelta(days=2),
                deadline=today + timedelta(days=6),
                status=TaskStatus.TO_DO.value,
                priority=9,
                recurring=0,
                tag="audit",
                project_id=3,
                active=True
            )
        ]
        
        session.add_all(tasks)
        session.flush()
        print(f"Created {len(tasks)} tasks")
        
        # Create subtasks
        print("Creating subtasks...")
        subtasks = [
            Task(
                id=7,
                title="Clear the area",
                description="Remove all items from the moving area",
                start_date=today,
                deadline=today,
                status=TaskStatus.TO_DO.value,
                priority=6,
                recurring=0,
                tag="logistics",
                project_id=1,
                active=True
            ),
            Task(
                id=8,
                title="Load tables into truck",
                description="Carefully load all tables",
                start_date=today,
                deadline=today,
                status=TaskStatus.TO_DO.value,
                priority=7,
                recurring=0,
                tag="logistics",
                project_id=1,
                active=True
            ),
            Task(
                id=9,
                title="Write test cases",
                description="Create comprehensive test scenarios",
                start_date=today + timedelta(days=1),
                deadline=today + timedelta(days=3),
                status=TaskStatus.IN_PROGRESS.value,
                priority=5,
                recurring=0,
                tag="testing",
                project_id=2,
                active=True
            ),
            Task(
                id=10,
                title="Review code quality",
                description="Check code standards and best practices",
                start_date=today + timedelta(days=4),
                deadline=today + timedelta(days=6),
                status=TaskStatus.TO_DO.value,
                priority=6,
                recurring=0,
                tag="development",
                project_id=2,
                active=True
            ),
        ]
        
        session.add_all(subtasks)
        session.flush()
        print(f"Created {len(subtasks)} subtasks")
        
        # Attach subtasks to parent tasks
        print("Attaching subtasks to parents...")
        parent_assignments = [
            ParentAssignment(parent_id=1, subtask_id=7),  # Moving tables -> Clear area
            ParentAssignment(parent_id=1, subtask_id=8),  # Moving tables -> Load tables
            ParentAssignment(parent_id=2, subtask_id=9),  # Testing task -> Write test cases
            ParentAssignment(parent_id=3, subtask_id=10),  # Code review -> Review code quality
        ]
        
        session.add_all(parent_assignments)
        session.flush()
        print(f"Attached {len(parent_assignments)} subtasks to parents")
        
        # Assign subtasks to users
        print("Assigning subtasks to users...")
        subtask_assignments = [
            TaskAssignment(task_id=7, user_id=cong_id),   # Clear area -> Cong
            TaskAssignment(task_id=8, user_id=cong_id),   # Load tables -> Cong
            TaskAssignment(task_id=9, user_id=julia_id),  # Write test cases -> Julia
            TaskAssignment(task_id=10, user_id=julia_id),  # Review code quality -> Julia
        ]
        
        session.add_all(subtask_assignments)
        session.flush()
        print(f"Assigned {len(subtask_assignments)} subtasks to users")
        
        # Create task assignments
        print("Creating task assignments...")
        assignments = [
            # Cong's assignments
            TaskAssignment(task_id=1, user_id=cong_id),
            TaskAssignment(task_id=4, user_id=cong_id),
            TaskAssignment(task_id=5, user_id=cong_id),  # Shared task
            TaskAssignment(task_id=6, user_id=cong_id),  # Completed task
            
            # Julia's assignments
            TaskAssignment(task_id=2, user_id=julia_id),
            TaskAssignment(task_id=3, user_id=julia_id),
            TaskAssignment(task_id=5, user_id=julia_id),  # Shared task
            TaskAssignment(task_id=12, user_id=julia_id),  # Bug investigation
            TaskAssignment(task_id=13, user_id=julia_id),  # API documentation
            TaskAssignment(task_id=11, user_id=julia_id),  # Design new feature
            TaskAssignment(task_id=14, user_id=julia_id),  # User research interview
            TaskAssignment(task_id=15, user_id=julia_id),  # Accessibility audit
        ]
        
        session.add_all(assignments)
        session.flush()
        print(f"Created {len(assignments)} task assignments")
        
        # Create comments
        print("Creating comments...")
        now = datetime.now()
        comments = [
            Comment(
                task_id=1,
                user_id=cong_id,
                comment="This task is straightforward, should be done soon.",
                timestamp=now - timedelta(hours=2)
            ),
            Comment(
                task_id=1,
                user_id=cong_id,
                comment="Actually, need more time for this.",
                timestamp=now - timedelta(hours=1)
            ),
            Comment(
                task_id=2,
                user_id=julia_id,
                comment="Starting work on this task.",
                timestamp=now - timedelta(hours=3)
            ),
            Comment(
                task_id=3,
                user_id=julia_id,
                comment="Blocked by dependency issue. Waiting for resolution.",
                timestamp=now - timedelta(hours=4)
            ),
            Comment(
                task_id=4,
                user_id=cong_id,
                comment="Documentation updates are progressing well.",
                timestamp=now - timedelta(minutes=30)
            ),
            Comment(
                task_id=5,
                user_id=manager_id,
                comment="Please coordinate on this shared task.",
                timestamp=now - timedelta(hours=5)
            ),
        ]
        
        session.add_all(comments)
        session.flush()
        print(f"Created {len(comments)} comments")
        
        # Commit all changes
        session.commit()
        print("✅ Database seed completed successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    seed_database()

