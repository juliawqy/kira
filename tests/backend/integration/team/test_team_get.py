import pytest
import tempfile
import os
from sqlalchemy import create_engine, delete
from unittest.mock import patch
from sqlalchemy.orm import sessionmaker
from backend.src.database.db_setup import Base
from backend.src.database.models.department import Department
from backend.src.handlers import department_handler as handler
from backend.src.database.models.team_assignment import TeamAssignment
from backend.src.database.models.user import User
from tests.mock_data.team_data import (
    VALID_TEAM_CREATE,
    VALID_SUBTEAM_CREATE,
    STAFF_USER,
    MANAGER_USER,
    NOT_FOUND_ID,
    DIRECTOR_USER,
    VALID_TEAM,
    VALID_SUBTEAM,
    VALID_DEPARTMENT,
)


@pytest.fixture(autouse=True)
def clean_db(test_engine):
    """Clean tables BEFORE each test"""
    TestingSession = sessionmaker(bind=test_engine, future=True)
    with TestingSession.begin() as s:
        s.execute(delete(TeamAssignment))
        s.execute(delete(Department))
        s.execute(delete(User))
    yield


@pytest.fixture(autouse=True)
def isolated_test_db():

    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    test_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine)

    with patch('backend.src.services.team.SessionLocal', TestSessionLocal), \
         patch('backend.src.services.department.SessionLocal', TestSessionLocal), \
         patch('backend.src.services.user.SessionLocal', TestSessionLocal), \
         patch('backend.src.handlers.department_handler.team_service.SessionLocal', TestSessionLocal), \
         patch('backend.src.handlers.department_handler.user_service.SessionLocal', TestSessionLocal), \
         patch('backend.src.handlers.department_handler.department_service.SessionLocal', TestSessionLocal):
        yield test_engine
 
    test_engine.dispose()
    try:
        os.unlink(db_path)
    except (OSError, PermissionError):
        pass 


@pytest.fixture(autouse=True)
def seed_user_and_dept(test_engine):
    """Insert a user and department to satisfy comment foreign keys."""
    from backend.src.services.team import SessionLocal as TestingSessionLocal
    with TestingSessionLocal.begin() as db:
        staff = User(**STAFF_USER)
        manager = User(**MANAGER_USER)
        director = User(**DIRECTOR_USER)
        db.add_all([staff, manager, director]) 
        db.flush() 
        dept_payload = {**VALID_DEPARTMENT, "manager_id": manager.user_id}
        dept = Department(**dept_payload)
        db.add(dept)
        db.flush()
    

# INT-139/001
def test_get_users_in_team():

    team = handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"], 
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    handler.assign_user_to_team(VALID_TEAM["team_id"], STAFF_USER["user_id"], MANAGER_USER["user_id"])
    handler.assign_user_to_team(VALID_TEAM["team_id"], MANAGER_USER["user_id"], DIRECTOR_USER["user_id"])

    users = handler.get_users_in_team(VALID_TEAM["team_id"])
    assert isinstance(users, list)
    assert len(users) == 2
    assert STAFF_USER["user_id"] in [user["user_id"] for user in users]
    assert MANAGER_USER["user_id"] in [user["user_id"] for user in users]


# INT-139/002
def test_get_users_in_team_not_found():

    team = handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"], 
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    handler.assign_user_to_team(VALID_TEAM["team_id"], STAFF_USER["user_id"], MANAGER_USER["user_id"])
    handler.assign_user_to_team(VALID_TEAM["team_id"], MANAGER_USER["user_id"], DIRECTOR_USER["user_id"])

    with pytest.raises(ValueError) as exc:
        handler.get_users_in_team(NOT_FOUND_ID)
    assert "not found" in str(exc.value)


# INT-139/003
def test_get_teams_of_user():

    team = handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"], 
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    subteam = handler.create_team_under_team(
        VALID_SUBTEAM_CREATE["team_id"],
        VALID_SUBTEAM_CREATE["team_name"],
        VALID_SUBTEAM_CREATE["manager_id"]
    )

    handler.assign_user_to_team(VALID_TEAM["team_id"], STAFF_USER["user_id"], MANAGER_USER["user_id"])
    handler.assign_user_to_team(VALID_SUBTEAM["team_id"], STAFF_USER["user_id"], MANAGER_USER["user_id"])

    teams = handler.get_teams_of_user(STAFF_USER["user_id"])

    assert isinstance(teams, list)
    assert len(teams) == 2
    assert VALID_TEAM["team_id"] in [team["team_id"] for team in teams]
    assert VALID_SUBTEAM["team_id"] in [team["team_id"] for team in teams]


# INT-139/004
def test_get_teams_of_user_not_found():

    team = handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"], 
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    subteam = handler.create_team_under_team(
        VALID_SUBTEAM_CREATE["team_id"],
        VALID_SUBTEAM_CREATE["team_name"],
        VALID_SUBTEAM_CREATE["manager_id"]
    )

    handler.assign_user_to_team(VALID_TEAM["team_id"], STAFF_USER["user_id"], MANAGER_USER["user_id"])
    handler.assign_user_to_team(VALID_SUBTEAM["team_id"], STAFF_USER["user_id"], MANAGER_USER["user_id"])


    with pytest.raises(ValueError) as exc:
        handler.get_teams_of_user(NOT_FOUND_ID)
    assert "not found" in str(exc.value)


# INT-139/005
def test_get_team_by_manager():

    team = handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"], 
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    subteam = handler.create_team_under_team(
        VALID_SUBTEAM_CREATE["team_id"],
        VALID_SUBTEAM_CREATE["team_name"],
        VALID_SUBTEAM_CREATE["manager_id"]
    )

    teams = handler.get_team_by_manager(MANAGER_USER["user_id"])

    assert isinstance(teams, list)
    assert len(teams) == 2

# INT-139/006
def test_get_team_by_manager_not_found():
    
    team = handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"], 
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    subteam = handler.create_team_under_team(
        VALID_SUBTEAM_CREATE["team_id"],
        VALID_SUBTEAM_CREATE["team_name"],
        VALID_SUBTEAM_CREATE["manager_id"]
    )

    with pytest.raises(ValueError) as exc:
        handler.get_team_by_manager(NOT_FOUND_ID)

    print("huhhh", exc.value)
    assert "not found" in str(exc.value)
