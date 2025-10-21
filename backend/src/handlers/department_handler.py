# backend/src/handlers/department_handler.py
from backend.src.services import department as dept_service
from backend.src.services import team as team_service


def view_teams_in_department(department_id: int):
    department = dept_service.get_department_by_id(department_id)
    if not department:
        raise ValueError(f"Department {department_id} not found")

    teams = team_service.get_teams_by_department(department_id)
    return teams

def add_team_to_department(department_id: int, team_name: str, team_number: int, manager_id: int):
    department = dept_service.get_department_by_id(department_id)
    if not department:
        raise ValueError(f"Department {department_id} not found")

    team = team_service.create_team(
        team_name=team_name,
        department_id=department_id,
        team_number=team_number,
        manager_id=manager_id
    )
    return team

def add_team_to_team(department_id: int, team_name: str, team_number: int):
    department = dept_service.get_department(department_id)
    if not department:
        raise ValueError(f"Department {department_id} not found")

    team = team_service.create_team(
        team_name=team_name,
        department_id=department_id,
        team_number=team_number
    )
    return team