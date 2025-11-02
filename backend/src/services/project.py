from typing import Dict
from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.project import Project, ProjectAssignment
from backend.src.enums.user_role import UserRole
from backend.src.database.models.user import User
def create_project(project_name: str, user_id) -> Dict:
    """Create a project. Only managers can create projects."""

    with SessionLocal.begin() as session:
        project_name_clean = project_name.strip()
        project = Project(
            project_name=project_name_clean,
            project_manager=user_id,
            active=True  
        )
        session.add(project)
        session.flush()
        session.refresh(project)

        return {
            "project_id": project.project_id,
            "project_name": project.project_name,
            "project_manager": project.project_manager,
            "active": project.active
        }

def get_project_by_id(project_id: int) -> Dict:
    """Return project details by id. Raises ValueError if not found."""
    with SessionLocal() as session:
        project = session.get(Project, project_id)
        if not project:
            return None

        return {
            "project_id": project.project_id,
            "project_name": project.project_name,
            "project_manager": project.project_manager,
            "active": project.active
        }

def get_projects_by_manager(project_manager_id: int) -> list[dict]:
    """Return all projects managed by a given manager."""
    with SessionLocal() as session:
        projects = session.query(Project).filter_by(project_manager=project_manager_id).all()
        result = []
        for proj in projects:
            result.append({
                "project_id": proj.project_id,
                "project_name": proj.project_name,
                "project_manager": proj.project_manager,
                "active": proj.active
            })
        return result

def assign_user_to_project(project_id: int, user_id: int) -> dict:
    """Assign a user to a project. No role restrictions."""
    with SessionLocal.begin() as session:

        existing = session.query(ProjectAssignment).filter_by(
            project_id=project_id,
            user_id=user_id
        ).first()
        if existing:
            raise ValueError("User already assigned to this project.")

        assignment = ProjectAssignment(project_id=project_id, user_id=user_id)
        session.add(assignment)

        return {
            "project_id": project_id,
            "user_id": user_id,
            "status": "assigned"
        }