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
    VALID_DEPARTMENT,
    MANAGER_USER,
    DIRECTOR_USER,
    VALID_TEAM,
    VALID_SUBTEAM,
    INVALID_CREATE_INVALID_DEPARTMENT_ID,
    INVALID_CREATE_INVALID_TEAM_ID,
    INVALID_CREATE_INVALID_MANAGER_ID,
    INVALID_CREATE_INVALID_SUBTEAM_MANAGER_ID,
    INVALID_CREATE_TEAM_UNAUTHORISED,
    INVALID_CREATE_SUBTEAM_UNAUTHORISED
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

# INT-058/001
def test_create_team_under_department():

    team = handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"], 
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    assert team["team_name"] == VALID_TEAM["team_name"]
    assert team["manager_id"] == VALID_TEAM["manager_id"]
    assert team["department_id"] == VALID_TEAM["department_id"]
    assert team["team_number"] == VALID_TEAM["team_number"]

# INT-058/002
def test_create_team_under_team():
    parent_team = handler.create_team_under_department(**VALID_TEAM_CREATE)

    sub_team = handler.create_team_under_team(
        VALID_SUBTEAM_CREATE["team_id"],
        VALID_SUBTEAM_CREATE["team_name"],
        VALID_SUBTEAM_CREATE["manager_id"]
    )

    assert sub_team["team_id"] == VALID_SUBTEAM["team_id"]
    assert sub_team["team_name"] == VALID_SUBTEAM["team_name"]
    assert sub_team["manager_id"] == VALID_SUBTEAM["manager_id"]
    assert sub_team["department_id"] == VALID_SUBTEAM["department_id"]
    assert sub_team["team_number"] == VALID_SUBTEAM["team_number"]

# INT-058/003
def test_create_team_invalid_department():
    with pytest.raises(ValueError) as exc:
        handler.create_team_under_department(
            INVALID_CREATE_INVALID_DEPARTMENT_ID["department_id"],
            INVALID_CREATE_INVALID_DEPARTMENT_ID["team_name"],
            INVALID_CREATE_INVALID_DEPARTMENT_ID["manager_id"]
        )
    assert "not found" in str(exc.value)

# INT-058/004
def test_create_subteam_invalid_parent_team():
    with pytest.raises(ValueError) as exc:
        handler.create_team_under_team(
            INVALID_CREATE_INVALID_TEAM_ID["team_id"],
            INVALID_CREATE_INVALID_TEAM_ID["team_name"],
            INVALID_CREATE_INVALID_TEAM_ID["manager_id"]
        )
    assert "not found" in str(exc.value)

# INT-058/005
def test_create_team_manager_not_found():
    with pytest.raises(ValueError) as exc:
        handler.create_team_under_department(
            INVALID_CREATE_INVALID_MANAGER_ID["department_id"],
            INVALID_CREATE_INVALID_MANAGER_ID["team_name"],
            INVALID_CREATE_INVALID_MANAGER_ID["manager_id"]
        )

    assert "not found" in str(exc.value)

# INT-058/006
def test_create_subteam_manager_not_found():

    team = handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"], 
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    with pytest.raises(ValueError) as exc:
        handler.create_team_under_team(
            INVALID_CREATE_INVALID_SUBTEAM_MANAGER_ID["team_id"],
            INVALID_CREATE_INVALID_SUBTEAM_MANAGER_ID["team_name"],
            INVALID_CREATE_INVALID_SUBTEAM_MANAGER_ID["manager_id"]
        )

    assert "not found" in str(exc.value)

# INT-058/007
def test_create_team_unauthorised_manager_role():
    with pytest.raises(ValueError) as exc:
        handler.create_team_under_department(
            INVALID_CREATE_TEAM_UNAUTHORISED["department_id"],
            INVALID_CREATE_TEAM_UNAUTHORISED["team_name"],
            INVALID_CREATE_TEAM_UNAUTHORISED["manager_id"]
        )
    assert "does not have permission" in str(exc.value)

# INT-058/008
def test_create_subteam_unauthorised_manager_role():

    team = handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"], 
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    with pytest.raises(ValueError) as exc:
        handler.create_team_under_team(
            INVALID_CREATE_SUBTEAM_UNAUTHORISED["team_id"],
            INVALID_CREATE_SUBTEAM_UNAUTHORISED["team_name"],
            INVALID_CREATE_SUBTEAM_UNAUTHORISED["manager_id"]
        )
    assert "does not have permission" in str(exc.value)