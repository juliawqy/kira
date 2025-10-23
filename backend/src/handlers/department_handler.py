# backend/src/handlers/department_handler.py
from backend.src.services import department as dept_service
from backend.src.services import team as team_service


def view_teams_in_department(department_id: int):
    department = dept_service.get_department_by_id(department_id)
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
    department = dept_service.get_department_by_id(department_id)
    if not department:
        raise ValueError(f"Department {department_id} not found")

    team = team_service.create_team(team_name, manager_id, department_id, str(department_id).zfill(2))

    return team

def create_team_under_team(team_id: int, team_name: str, manager_id: int):
    team = team_service.get_team_by_id(team_id)
    if not team:
        raise ValueError(f"Team {team_id} not found")

    subteam = team_service.create_team(
        team_name=team_name,
        user_id=manager_id,
        department_id=team["department_id"],
        prefix=team["team_number"][0:4]
    )
    return subteam