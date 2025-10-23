import pytest
import importlib
import tempfile
import os
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch
from backend.src.database.db_setup import Base
from backend.src.handlers import department_handler
from backend.src.services import team as team_service
from backend.src.database.models.user import User
from backend.src.database.models.team import Team
from backend.src.database.models.department import Department
from backend.src.database.models.team_assignment import TeamAssignment
from tests.mock_data.team_data import (
    STAFF_USER, 
    MANAGER_USER, 
    DIRECTOR_USER,
    VALID_TEAM_CREATE, 
    VALID_TEAM, 
    VALID_SUBTEAM_CREATE, 
    VALID_SUBTEAM, 
    NOT_FOUND_ID,
    INVALID_TEAM_NUMBER
)
from tests.mock_data.department_data import (
    VALID_DEPARTMENT_1, 
    INVALID_DEPARTMENT_ID
)


@pytest.fixture(autouse=True)
def clean_db(test_engine):
    """Clean tables BEFORE each test"""
    TestingSession = sessionmaker(bind=test_engine, future=True)
    with TestingSession.begin() as s:
        s.execute(delete(TeamAssignment))
        s.execute(delete(Team))
        s.execute(delete(Department))
        s.execute(delete(User))
    yield


@pytest.fixture
def isolated_test_db():
    """Create isolated SQLite DB and patch all service SessionLocals"""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    test_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine)

    with patch('backend.src.services.team.SessionLocal', TestSessionLocal), \
         patch('backend.src.services.department.SessionLocal', TestSessionLocal), \
         patch('backend.src.handlers.department_handler.dept_service.SessionLocal', TestSessionLocal), \
         patch('backend.src.handlers.department_handler.team_service.SessionLocal', TestSessionLocal):

        

        department_handler = importlib.import_module("backend.src.handlers.department_handler")
        yield test_engine, team_service, department_handler

    test_engine.dispose()
    try:
        os.unlink(db_path)
    except (OSError, PermissionError):
        pass


@pytest.fixture(autouse=True)
def seed_users_and_department(isolated_test_db):
    """Seed default users and one department"""
    test_engine, _, _ = isolated_test_db
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        db.add_all([
            User(**STAFF_USER),
            User(**MANAGER_USER),
            User(**DIRECTOR_USER),
            Department(**VALID_DEPARTMENT_1)
        ])


# INT-104/001
def test_view_team_by_department(isolated_test_db):

    department_handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"],
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    teams = department_handler.view_teams_in_department(VALID_DEPARTMENT_1["department_id"])
    print("fml:", teams)
    assert isinstance(teams, list)
    assert len(teams) == 1
    assert teams[0]["team_name"] == VALID_TEAM_CREATE["team_name"]


# INT-104/002
def test_view_team_by_nonexistent_department(isolated_test_db):
    with pytest.raises(ValueError):
        department_handler.view_teams_in_department(INVALID_DEPARTMENT_ID)

# INT-104/003
def test_view_subteam_by_team(isolated_test_db):

    department_handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"],
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    department_handler.create_team_under_team(
        VALID_SUBTEAM_CREATE["team_id"],
        VALID_SUBTEAM_CREATE["team_name"],
        VALID_SUBTEAM_CREATE["manager_id"]
    )

    subteams = department_handler.view_subteams_in_team(VALID_TEAM["team_id"])

    assert isinstance(subteams, list)
    assert len(subteams) == 1
    assert subteams[0]["team_name"] == VALID_SUBTEAM["team_name"]
    assert subteams[0]["manager_id"] == VALID_SUBTEAM["manager_id"]
    assert subteams[0]["department_id"] == VALID_SUBTEAM["department_id"]
    assert subteams[0]["team_number"] == VALID_SUBTEAM["team_number"]


# INT-104/004
def test_view_subteam_by_invalid_team(isolated_test_db):

    with pytest.raises(ValueError):
        department_handler.view_subteams_in_team(INVALID_TEAM_NUMBER)


# INT-104/005
def test_view_team_by_department_empty(isolated_test_db):

    teams = department_handler.view_teams_in_department(VALID_DEPARTMENT_1["department_id"])
    assert teams == []


# INT-104/006
def test_view_team_by_team_empty(isolated_test_db):

    department_handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"],
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    subteams = department_handler.view_subteams_in_team(VALID_TEAM["team_id"])
    assert subteams == []


# INT-104/007
def test_create_team_under_department_success(isolated_test_db):
    team = department_handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"],
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    assert team["team_id"] == VALID_TEAM["team_id"]
    assert team["team_name"] == VALID_TEAM["team_name"]
    assert team["manager_id"] == VALID_TEAM["manager_id"]
    assert team["department_id"] == VALID_TEAM["department_id"]
    assert team["team_number"] == VALID_TEAM["team_number"]


# INT-104/008
def test_create_team_under_nonexistent_department(isolated_test_db):
    with pytest.raises(ValueError):
        department_handler.create_team_under_department(INVALID_DEPARTMENT_ID, VALID_TEAM_CREATE["team_name"], VALID_TEAM_CREATE["manager_id"])


# INT-104/009
def test_create_team_under_team_success(isolated_test_db):
    from backend.src.services import team as team_service

    department_handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"],
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    subteam = department_handler.create_team_under_team(
        VALID_SUBTEAM_CREATE["team_id"],
        VALID_SUBTEAM_CREATE["team_name"],
        VALID_SUBTEAM_CREATE["manager_id"]
    )

    assert subteam["team_id"] == VALID_SUBTEAM["team_id"]
    assert subteam["team_name"] == VALID_SUBTEAM["team_name"]
    assert subteam["manager_id"] == VALID_SUBTEAM["manager_id"]
    assert subteam["department_id"] == VALID_SUBTEAM["department_id"]
    assert subteam["team_number"] == VALID_SUBTEAM["team_number"]


# INT-104/010
def test_create_team_under_nonexistent_team(isolated_test_db):
    with pytest.raises(ValueError):
        department_handler.create_team_under_team(NOT_FOUND_ID, VALID_SUBTEAM_CREATE["team_name"], VALID_SUBTEAM_CREATE["manager_id"])
