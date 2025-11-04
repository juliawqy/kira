from backend.src.services import project as project_service
from backend.src.services import user as user_service
from backend.src.enums.user_role import UserRole

def create_project(project_name: str, project_manager_id: int = None):
    user_role = user_service.get_user(project_manager_id)
    if str(getattr(user_role, "role", "")).lower() != (UserRole.MANAGER.value.lower() or UserRole.DIRECTOR.value.lower()):
        raise ValueError(f"User {project_manager_id} cannot create a project.")
    
    if not project_name or not project_name.strip():
        raise ValueError("Project name cannot be empty or whitespace.")

    project = project_service.create_project(project_name, project_manager_id)
    return project

def get_project_by_id(project_id: int):
    project = project_service.get_project_by_id(project_id)
    if not project:
        raise ValueError("Project not found.")
    return project

def get_projects_by_manager(project_manager_id: int):
    """Get all projects managed by a specific manager."""
    return project_service.get_projects_by_manager(project_manager_id)


# -------- Project x User Handlers -------------------------------------------------------


def assign_user_to_project(project_id: int, user_id: int, assigner_id: int = None):
    project = project_service.get_project_by_id(project_id)
    if not project:
        raise ValueError("Project not found.")
    user = user_service.get_user(user_id)
    if not user:
        raise ValueError("User not found.")
    
    assigner = user_service.get_user(assigner_id)
    if assigner.role not in [UserRole.MANAGER, UserRole.DIRECTOR]:
        raise ValueError("User does not have permission to assign users.")

    assignment = project_service.assign_user_to_project(project_id, user_id)
    return assignment