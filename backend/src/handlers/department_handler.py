# backend/src/handlers/department_handler.py
from backend.src.services import department as department_service
from backend.src.services import team as team_service
from backend.src.services import user as user_service
from backend.src.enums.user_role import UserRole


def view_teams_in_department(department_id: int):
    department = department_service.get_department_by_id(department_id)
    if not department:
        raise ValueError(f"Department {department_id} not found")

    teams = team_service.get_teams_by_department(department_id)
    return teams

def view_subteams_in_team(team_id: int):
    team = team_service.get_team_by_id(team_id)
    if not team:
        raise ValueError(f"Team {team_id} not found")

    subteams = team_service.get_subteam_by_team_number(team["team_number"])

    return subteams

def create_team_under_department(department_id: int, team_name: str, manager_id: int):
    department = department_service.get_department_by_id(department_id)
    if not department:
        raise ValueError(f"Department {department_id} not found")
    
    user = user_service.get_user(manager_id)
    if not user:
        raise ValueError(f"User {manager_id} not found")
    if user.role not in [UserRole.MANAGER.value, UserRole.DIRECTOR.value]:
        raise ValueError(f"User {manager_id} does not have permission to manage a team")

    team = team_service.create_team(team_name, manager_id, department_id, str(department_id).zfill(2))

    return team

def create_team_under_team(team_id: int, team_name: str, manager_id: int):
    team = team_service.get_team_by_id(team_id)
    if not team:
        raise ValueError(f"Team {team_id} not found")
    
    user = user_service.get_user(manager_id)
    if not user:
        raise ValueError(f"User {manager_id} not found")
    if user.role not in [UserRole.MANAGER.value, UserRole.DIRECTOR.value]:
        raise ValueError(f"User {manager_id} does not have permission to manage a team")

    subteam = team_service.create_team(
        team_name=team_name,
        user_id=manager_id,
        department_id=team["department_id"],
        prefix=team["team_number"][0:4]
    )
    return subteam


def view_users_in_department(department_id: int):
    department = department_service.get_department_by_id(department_id)
    if not department:
        raise ValueError(f"Department {department_id} not found")

    users = user_service.get_users_by_department(department_id)
    return [
        {
            "user_id": u.user_id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "admin": u.admin,
        }
        for u in users
    ]


def assign_user_to_team(team_id: int, user_id: int, manager_id: int):
    team = team_service.get_team_by_id(team_id)
    if not team:
        raise ValueError(f"Team {team_id} not found")
    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    manager = user_service.get_user(manager_id)
    if not manager:
        raise ValueError(f"User {manager_id} not found")
    if manager.role not in [UserRole.MANAGER.value, UserRole.DIRECTOR.value]:
        raise ValueError(f"User {manager_id} does not have permission to assign users to a team")

    return team_service.assign_to_team(team_id, user_id)


def get_users_in_team(team_id: int):
    team = team_service.get_team_by_id(team_id)
    if not team:
        raise ValueError(f"Team {team_id} not found")

    return team_service.get_users_in_team(team_id)


def get_teams_of_user(user_id: int):
    user = user_service.get_user(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    return team_service.get_teams_of_user(user_id)


def get_team_by_manager(manager_id: int):
    user = user_service.get_user(manager_id)
    if not user:
        raise ValueError(f"User {manager_id} not found")

    return team_service.get_team_by_manager(manager_id)