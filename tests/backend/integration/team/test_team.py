import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.database.db_setup import Base
from backend.src.services import team as team_service
from tests.mock_data.team_data import VALID_TEAM_CREATE, STAFF_USER, MANAGER_USER, NOT_FOUND_ID, DIRECTOR_USER
from unittest.mock import patch
from backend.src.database.models.team import TeamAssignment
from sqlalchemy.orm import Session


@pytest.fixture(autouse=True)
def isolated_test_db():

    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Create test engine
    test_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session factory
    TestSessionLocal = sessionmaker(bind=test_engine)
    
    # Patch the service layer to use our test database
    with patch('backend.src.services.team.SessionLocal', TestSessionLocal):
        yield test_engine
    
    # Cleanup: Close engine and remove temp file
    test_engine.dispose()
    try:
        os.unlink(db_path)
    except (OSError, PermissionError):
        pass  # File might already be cleaned up

# INT-084/001
def test_create_and_get_team(isolated_test_db):
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], manager, department_id=VALID_TEAM_CREATE.get("department_id"), team_number=VALID_TEAM_CREATE.get("team_number")
    )

    assert team["team_name"] == VALID_TEAM_CREATE["team_name"]
    assert team["manager_id"] == manager.user_id

    fetched = team_service.get_team_by_id(team["team_id"])
    assert fetched["team_id"] == team["team_id"]
    assert fetched["team_name"] == team["team_name"]

# INT-084/002
def test_create_team_integration_non_manager_raises(isolated_test_db):
    staff = type("U", (), {"user_id": STAFF_USER["user_id"], "role": STAFF_USER["role"]})()
    # Non-manager should not be allowed to create a team
    with pytest.raises(ValueError) as exc:
        team_service.create_team(
            VALID_TEAM_CREATE["team_name"],
            staff,
            department_id=VALID_TEAM_CREATE.get("department_id"),
            team_number=VALID_TEAM_CREATE.get("team_number"),
        )
    assert "Only managers" in str(exc.value)

# INT-084/003
def test_create_team_integration_empty_name_raises(isolated_test_db):
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    with pytest.raises(ValueError):
        team_service.create_team(
            "   ",
            manager,
            department_id=VALID_TEAM_CREATE.get("department_id"),
            team_number=VALID_TEAM_CREATE.get("team_number"),
        )

# INT-084/004
def test_get_team_integration_not_found(isolated_test_db):
    with pytest.raises(ValueError):
        team_service.get_team_by_id(NOT_FOUND_ID)


# INT-084/005
def test_assign_to_team_integration_not_found(isolated_test_db):
    # Attempt to assign to a team id that doesn't exist should raise
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    with pytest.raises(ValueError) as exc:
        team_service.assign_to_team(NOT_FOUND_ID, 10, manager)
    assert f"Team with id {NOT_FOUND_ID} not found" in str(exc.value)


# INT-084/006
def test_assign_to_team_persists_assignment(isolated_test_db):
    # Create manager and a team
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], manager,
        department_id=VALID_TEAM_CREATE.get("department_id"),
        team_number=VALID_TEAM_CREATE.get("team_number"),
    )

    # Assign a user to the team
    assignee_id = 123
    result = team_service.assign_to_team(team["team_id"], assignee_id, manager)

    assert result["team_id"] == team["team_id"]
    assert result["user_id"] == assignee_id
    assert result["assigned_by"] == manager.user_id

    # Verify the assignment exists in the DB
    sess = Session(bind=isolated_test_db)
    try:
        assignment = sess.query(TeamAssignment).filter_by(team_id=team["team_id"], user_id=assignee_id).one_or_none()
        assert assignment is not None
    finally:
        sess.close()


# INT-084/006
def test_director_can_assign(isolated_test_db):
    # Create manager-owned team, director assigns
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], manager,
        department_id=VALID_TEAM_CREATE.get("department_id"),
        team_number=VALID_TEAM_CREATE.get("team_number"),
    )

    director = type("U", (), {"user_id": DIRECTOR_USER["user_id"], "role": DIRECTOR_USER["role"]})()
    assignee_id = 222
    result = team_service.assign_to_team(team["team_id"], assignee_id, director)
    assert result["team_id"] == team["team_id"]
    assert result["user_id"] == assignee_id


# INT-084/007
def test_unauthorized_user_cannot_assign(isolated_test_db):
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], manager,
        department_id=VALID_TEAM_CREATE.get("department_id"),
        team_number=VALID_TEAM_CREATE.get("team_number"),
    )

    staff = type("U", (), {"user_id": STAFF_USER["user_id"], "role": STAFF_USER["role"]})()
    with pytest.raises(ValueError):
        team_service.assign_to_team(team["team_id"], 999, staff)


# INT-084/008
def test_duplicate_assignment_raises_and_only_one_record_exists(isolated_test_db):
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], manager,
        department_id=VALID_TEAM_CREATE.get("department_id"),
        team_number=VALID_TEAM_CREATE.get("team_number"),
    )

    assignee_id = 55
    # First assignment should succeed
    team_service.assign_to_team(team["team_id"], assignee_id, manager)

    # Second assignment of same user to same team should raise due to unique constraint handled in service
    with pytest.raises(ValueError):
        team_service.assign_to_team(team["team_id"], assignee_id, manager)

    # Verify only one record exists
    sess = Session(bind=isolated_test_db)
    try:
        assignments = sess.query(TeamAssignment).filter_by(team_id=team["team_id"], user_id=assignee_id).all()
        assert len(assignments) == 1
    finally:
        sess.close()



