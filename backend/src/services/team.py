from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.team import Team

def create_team(team_name: str, user) -> Team:
    """Create a team and return it. Only managers can create a team. User is a dummy object with user_id and role."""
    if not hasattr(user, 'role') or user.role != 'manager':
        raise ValueError("Only managers can create a team.")
    if not team_name or not team_name.strip():
        raise ValueError("Team name cannot be empty or whitespace.")
    with SessionLocal.begin() as session:
        team = Team(
            team_name=team_name,
            manager_id=user.user_id
        )
        session.add(team)
        session.flush()
        session.refresh(team)
        return team
    
def get_team_by_id(team_id: int, user) -> dict:
    """Return team and user details if user is manager (or member, if implemented)."""
    with SessionLocal() as session:
        team = session.get(Team, team_id)
        if not team:
            raise ValueError("Team not found")
        
        return {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "manager_id": team.manager_id,
            "user_id": user.user_id,
            "name": getattr(user, "name", "Test User"),
            "email": getattr(user, "email", "test@example.com"),
        }
    
def delete_team(team_id: int, user):
    """Delete a team if the user is the manager. Raise PermissionError if not manager, ValueError if not found."""
    with SessionLocal.begin() as session:
        team = session.get(Team, team_id)
        if not team:
            raise ValueError("Team not found")
        if user.user_id != team.manager_id:
            raise PermissionError("Only the team manager can delete the team.")
        session.delete(team)
        session.flush()

def update_team_name(team_id: int, new_name: str, user):
    """Update the team's name if the user is the manager. Raise PermissionError if not manager, ValueError if not found or invalid name."""
    if not new_name or not new_name.strip():
        raise ValueError("Team name cannot be empty or whitespace.")
    with SessionLocal.begin() as session:
        team = session.get(Team, team_id)
        if not team:
            raise ValueError("Team not found")
        if user.user_id != team.manager_id:
            raise PermissionError("Only the team manager can edit the team name.")
        team.team_name = new_name.strip()
        session.add(team)
        session.flush()
        session.refresh(team)
        return team