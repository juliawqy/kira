import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.database.db_setup import Base
from backend.src.services import team as team_service
from tests.mock_data.team_data import (
    VALID_TEAM_CREATE,
    STAFF_USER,
    MANAGER_USER,
    NOT_FOUND_ID,
    DIRECTOR_USER,
    ASSIGNEE_ID_123,
    ASSIGNEE_ID_222,
    ASSIGNEE_ID_55,
    ASSIGNEE_ID_999,
)
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

# INT-058/001
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

# INT-058/002
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

# INT-058/003
def test_create_team_integration_empty_name_raises(isolated_test_db):
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    with pytest.raises(ValueError):
        team_service.create_team(
            "   ",
            manager,
            department_id=VALID_TEAM_CREATE.get("department_id"),
            team_number=VALID_TEAM_CREATE.get("team_number"),
        )

# INT-061/001
def test_get_team_integration_not_found(isolated_test_db):
    with pytest.raises(ValueError):
        team_service.get_team_by_id(NOT_FOUND_ID)


# INT-062/001
def test_assign_to_team_integration_not_found(isolated_test_db):
    # Attempt to assign to a team id that doesn't exist should raise
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    with pytest.raises(ValueError) as exc:
        team_service.assign_to_team(NOT_FOUND_ID, ASSIGNEE_ID_123, manager)
    assert f"Team with id {NOT_FOUND_ID} not found" in str(exc.value)


# INT-062/001
def test_assign_to_team_persists_assignment(isolated_test_db):
    # Create manager and a team
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], manager,
        department_id=VALID_TEAM_CREATE.get("department_id"),
        team_number=VALID_TEAM_CREATE.get("team_number"),
    )

    # Assign a user to the team
    assignee_id = ASSIGNEE_ID_123
    result = team_service.assign_to_team(team["team_id"], assignee_id, manager)

    assert result["team_id"] == team["team_id"]
    assert result["user_id"] == assignee_id
    assert "id" in result and result["id"] is not None

    # Verify the assignment exists in the DB
    sess = Session(bind=isolated_test_db)
    try:
        assignment = sess.query(TeamAssignment).filter_by(team_id=team["team_id"], user_id=assignee_id).one_or_none()
        assert assignment is not None
    finally:
        sess.close()


# INT-062/002
def test_director_can_assign(isolated_test_db):
    # Create manager-owned team, director assigns
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], manager,
        department_id=VALID_TEAM_CREATE.get("department_id"),
        team_number=VALID_TEAM_CREATE.get("team_number"),
    )

    director = type("U", (), {"user_id": DIRECTOR_USER["user_id"], "role": DIRECTOR_USER["role"]})()
    assignee_id = ASSIGNEE_ID_222
    result = team_service.assign_to_team(team["team_id"], assignee_id, director)
    assert result["team_id"] == team["team_id"]
    assert result["user_id"] == assignee_id


# INT-062/003
def test_unauthorized_user_cannot_assign(isolated_test_db):
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], manager,
        department_id=VALID_TEAM_CREATE.get("department_id"),
        team_number=VALID_TEAM_CREATE.get("team_number"),
    )

    staff = type("U", (), {"user_id": STAFF_USER["user_id"], "role": STAFF_USER["role"]})()
    with pytest.raises(ValueError):
        team_service.assign_to_team(team["team_id"], ASSIGNEE_ID_999, staff)


# INT-062/004
def test_duplicate_assignment_raises_and_only_one_record_exists(isolated_test_db):
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], manager,
        department_id=VALID_TEAM_CREATE.get("department_id"),
        team_number=VALID_TEAM_CREATE.get("team_number"),
    )

    assignee_id = ASSIGNEE_ID_55
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

# INT-062/005
def test_assign_with_nonexistent_user_id_creates_assignment(isolated_test_db):
    """Assigning an arbitrary (non-existent) user_id should create a TeamAssignment record.

    The project uses a simple integration DB for tests; we don't create a users row here.
    The service inserts the assignment row (FK constraints depend on SQLite PRAGMA); assert the row exists.
    """
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()

    # Manager creates a team
    team = team_service.create_team("Team for invalid user test", manager, department_id=VALID_TEAM_CREATE["department_id"], team_number=VALID_TEAM_CREATE["team_number"])

    # Use an arbitrary user id that doesn't exist in users table
    invalid_user_id = ASSIGNEE_ID_999
    result = team_service.assign_to_team(team["team_id"], invalid_user_id, manager)

    assert result["team_id"] == team["team_id"]
    assert result["user_id"] == invalid_user_id

    # Verify assignment exists in DB
    sess = Session(bind=isolated_test_db)
    try:
        a = sess.query(TeamAssignment).filter_by(team_id=team["team_id"], user_id=invalid_user_id).one_or_none()
        assert a is not None
    finally:
        sess.close()


# INT-062/006
def test_manager_creates_team_and_assigns_member(isolated_test_db):
    """Manager creates a team and then assigns a member; verify persisted assignment."""
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()

    team = team_service.create_team("Manager create then assign", manager, department_id=VALID_TEAM_CREATE["department_id"] , team_number=VALID_TEAM_CREATE["team_number"])

    assignee = ASSIGNEE_ID_123
    result = team_service.assign_to_team(team["team_id"], assignee, manager)

    assert result["team_id"] == team["team_id"]
    assert result["user_id"] == assignee

    sess = Session(bind=isolated_test_db)
    try:
        assignment = sess.query(TeamAssignment).filter_by(team_id=team["team_id"], user_id=assignee).one_or_none()
        assert assignment is not None
    finally:
        sess.close()



