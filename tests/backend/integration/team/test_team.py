import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.database.db_setup import Base
from backend.src.services import team as team_service
from tests.mock_data.team_data import VALID_TEAM_CREATE, STAFF_USER, MANAGER_USER, NOT_FOUND_ID
from unittest.mock import patch


@pytest.fixture(autouse=True)
def isolated_test_db():
    """
    Create an isolated test database for each test.
    Uses a temporary database file that's automatically cleaned up.
    """
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


def test_create_and_get_team(isolated_test_db):
    # use mock manager data
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], manager, department_id=VALID_TEAM_CREATE.get("department_id"), team_number=VALID_TEAM_CREATE.get("team_number")
    )

    assert team["team_name"] == VALID_TEAM_CREATE["team_name"]
    assert team["manager_id"] == manager.user_id

    fetched = team_service.get_team_by_id(team["team_id"])
    assert fetched["team_id"] == team["team_id"]
    assert fetched["team_name"] == team["team_name"]


def test_create_team_integration_non_manager_raises(isolated_test_db):
    # use mock staff data
    staff = type("U", (), {"user_id": STAFF_USER["user_id"], "role": STAFF_USER["role"]})()
    # Non-manager should not be allowed to create a team
    with pytest.raises(ValueError) as exc:
        team_service.create_team(VALID_TEAM_CREATE["team_name"], staff)
    assert "Only managers" in str(exc.value)


def test_create_team_integration_empty_name_raises(isolated_test_db):
    manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
    with pytest.raises(ValueError):
        team_service.create_team("   ", manager)


def test_get_team_integration_not_found(isolated_test_db):
    # Ensure get_team_by_id raises when id is absent
    with pytest.raises(ValueError):
        team_service.get_team_by_id(NOT_FOUND_ID)
        