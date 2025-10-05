from typing import Dict
from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.project import Project
from backend.src.enums.user_role import UserRole

def create_project(project_name: str, user) -> Dict:
    """Create a project. Only managers can create projects."""
    user_role = getattr(user, "role", None)
    if not user_role or str(user_role).lower() != UserRole.MANAGER.value.lower():
        raise ValueError("Only managers can create a project.")

    if not project_name or not project_name.strip():
        raise ValueError("Project name cannot be empty or whitespace.")

    with SessionLocal.begin() as session:
        project_name_clean = project_name.strip()
        project = Project(
            project_name=project_name_clean,
            project_manager=user.user_id,
            active=True  # permanently true for now
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
            raise ValueError("Project not found")

        return {
            "project_id": project.project_id,
            "project_name": project.project_name,
            "project_manager": project.project_manager,
            "active": project.active
        }
