import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.database.db_setup import Base
from backend.src.handlers import project_handler as project_handler
from backend.src.database.models.user import User
from unittest.mock import patch
from tests.mock_data.project_data import (
    VALID_PROJECT_NAME,
    MANAGER_USER,
    STAFF_USER,
    VALID_PROJECT,
    NOT_FOUND_ID,
)

@pytest.fixture(scope="function")
def test_engine():
    """Create and destroy a fresh SQLite database for each test."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()
    os.remove(db_path)


@pytest.fixture(scope="function")
def isolated_test_db(test_engine):
    """Patch both services to use the fresh DB for each test."""
    TestSessionLocal = sessionmaker(bind=test_engine)
    with patch("backend.src.services.project.SessionLocal", TestSessionLocal), \
         patch("backend.src.services.user.SessionLocal", TestSessionLocal):
        yield test_engine

@pytest.fixture(autouse=True)
def seed_task_and_user(test_engine):
    """Insert a user to satisfy comment foreign keys."""
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        manager = User(**MANAGER_USER)
        staff = User(**STAFF_USER)
        db.add_all([manager, staff])
    yield


# INT-081/001
def test_assign_user_to_project_success(isolated_test_db):

    project = project_handler.create_project(VALID_PROJECT_NAME, MANAGER_USER["user_id"])
    result = project_handler.assign_user_to_project(VALID_PROJECT["project_id"], STAFF_USER["user_id"], MANAGER_USER["user_id"])

    assert result["project_id"] == VALID_PROJECT["project_id"]
    assert result["user_id"] == STAFF_USER["user_id"]

# INT-081/002
def test_duplicate_assignment_fails(isolated_test_db):

    project = project_handler.create_project(VALID_PROJECT_NAME, MANAGER_USER["user_id"])
    project_handler.assign_user_to_project(VALID_PROJECT["project_id"], STAFF_USER["user_id"], MANAGER_USER["user_id"])

    with pytest.raises(ValueError, match="already assigned"):
        project_handler.assign_user_to_project(VALID_PROJECT["project_id"], STAFF_USER["user_id"], MANAGER_USER["user_id"])

# INT-081/003
def test_assign_to_nonexistent_project_fails(isolated_test_db):
    with pytest.raises(ValueError, match="Project not found"):
        project_handler.assign_user_to_project(NOT_FOUND_ID, STAFF_USER["user_id"], MANAGER_USER["user_id"])

# INT-081/004
def test_assign_nonexistent_user_fails(isolated_test_db):

    project = project_handler.create_project(VALID_PROJECT_NAME, MANAGER_USER["user_id"])

    with pytest.raises(ValueError, match="User not found"):
        project_handler.assign_user_to_project(project["project_id"], NOT_FOUND_ID, MANAGER_USER["user_id"])

# INT-081/005
def test_assigner_without_permission_fails(isolated_test_db):

    project = project_handler.create_project(VALID_PROJECT_NAME, MANAGER_USER["user_id"])

    with pytest.raises(ValueError, match="does not have permission"):
        project_handler.assign_user_to_project(project["project_id"], STAFF_USER["user_id"], STAFF_USER["user_id"])