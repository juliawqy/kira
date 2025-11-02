"""Script to create test projects and tasks for report testing."""

# IMPORTANT: Import all models before creating any instances
# This ensures SQLAlchemy can resolve all relationships
from backend.src.database.db_setup import SessionLocal, Base, engine

# Import all models in the same order as main.py to ensure relationships resolve correctly
from backend.src.database.models.task import Task  
from backend.src.database.models.parent_assignment import ParentAssignment
from backend.src.database.models.team import Team
from backend.src.database.models.team_assignment import TeamAssignment
from backend.src.database.models.user import User
from backend.src.database.models.department import Department
from backend.src.database.models.project import Project, ProjectAssignment  
from backend.src.database.models.comment import Comment
from backend.src.database.models.task_assignment import TaskAssignment as TaskAssignmentModel

# Ensure all tables are registered (this triggers relationship resolution)
Base.metadata.create_all(bind=engine)

from backend.src.enums.task_status import TaskStatus
from backend.src.enums.user_role import UserRole
from datetime import date, timedelta

def create_test_project_with_tasks():
    """Create a test project with tasks in various statuses."""
    session = SessionLocal()
    
    try:
        # Create manager
        manager = User(
            name="Project Manager",
            email="pm@test.com",
            role=UserRole.MANAGER.value,
            hashed_pw="hashed_pw",
            admin=False,
            department_id=None
        )
        session.add(manager)
        session.flush()
        
        # Create project
        project = Project(
            project_name="Sample Project for Reports",
            project_manager=manager.user_id,
            active=True
        )
        session.add(project)
        session.flush()
        
        # Create tasks
        today = date.today()
        
        tasks_data = [
            {
                "title": "Project Planning",
                "description": "Plan the project milestones and deliverables",
                "status": TaskStatus.TO_DO.value,
                "priority": 8,
                "start_date": today + timedelta(days=1),
                "deadline": today + timedelta(days=7),
                "tag": "planning"
            },
            {
                "title": "Database Design",
                "description": "Design the database schema",
                "status": TaskStatus.TO_DO.value,
                "priority": 9,
                "start_date": today + timedelta(days=3),
                "deadline": today + timedelta(days=10),
                "tag": "design"
            },
            {
                "title": "API Development",
                "description": "Build REST API endpoints",
                "status": TaskStatus.IN_PROGRESS.value,
                "priority": 9,
                "start_date": today - timedelta(days=5),
                "deadline": today + timedelta(days=5),
                "tag": "development"
            },
            {
                "title": "Frontend Implementation",
                "description": "Create user interface components",
                "status": TaskStatus.IN_PROGRESS.value,
                "priority": 7,
                "start_date": today - timedelta(days=3),
                "deadline": today + timedelta(days=7),
                "tag": "frontend"
            },
            {
                "title": "Unit Tests",
                "description": "Write unit tests for backend",
                "status": TaskStatus.COMPLETED.value,
                "priority": 6,
                "start_date": today - timedelta(days=20),
                "deadline": today - timedelta(days=10),
                "tag": "testing"
            },
            {
                "title": "Documentation",
                "description": "Write API documentation",
                "status": TaskStatus.COMPLETED.value,
                "priority": 5,
                "start_date": today - timedelta(days=15),
                "deadline": today - timedelta(days=5),
                "tag": "docs"
            },
            {
                "title": "Code Review",
                "description": "Waiting for peer code review",
                "status": TaskStatus.BLOCKED.value,
                "priority": 8,
                "start_date": today - timedelta(days=2),
                "deadline": today + timedelta(days=3),
                "tag": "review"
            },
        ]
        
        # Create team members
        team_members = []
        for i in range(1, 4):
            member = User(
                name=f"Team Member {i}",
                email=f"member{i}@test.com",
                role=UserRole.STAFF.value,
                hashed_pw="hashed_pw",
                admin=False,
                department_id=None
            )
            team_members.append(member)
        
        session.add_all(team_members)
        session.flush()
        
        # Create tasks
        tasks = []
        for task_data in tasks_data:
            task_data["project_id"] = project.project_id
            task_data["active"] = True
            task = Task(**task_data)
            session.add(task)
            tasks.append(task)
        
        session.flush()
        
        # Assign team members to tasks
        # Task 0 (Projected) -> member 1
        session.add(TaskAssignmentModel(task_id=tasks[0].id, user_id=team_members[0].user_id))
        
        # Task 2 (In-Progress) -> members 1 and 2
        session.add(TaskAssignmentModel(task_id=tasks[2].id, user_id=team_members[0].user_id))
        session.add(TaskAssignmentModel(task_id=tasks[2].id, user_id=team_members[1].user_id))
        
        # Task 3 (In-Progress) -> member 3
        session.add(TaskAssignmentModel(task_id=tasks[3].id, user_id=team_members[2].user_id))
        
        # Task 4 (Completed) -> member 1
        session.add(TaskAssignmentModel(task_id=tasks[4].id, user_id=team_members[0].user_id))
        
        session.commit()
        
        print(f"✅ Created project '{project.project_name}' with ID: {project.project_id}")
        print(f"   - {len(tasks)} tasks created")
        print(f"   - {len(team_members)} team members created")
        print(f"\n📊 Test the report endpoints:")
        print(f"   PDF: http://localhost:8000/kira/app/api/v1/report/project/{project.project_id}/pdf")
        print(f"   Excel: http://localhost:8000/kira/app/api/v1/report/project/{project.project_id}/excel")
        print(f"\n🌐 Or use the frontend:")
        print(f"   Open frontend/report/export_report.html and enter project ID: {project.project_id}")
        
        return project.project_id
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error creating test data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    create_test_project_with_tasks()

