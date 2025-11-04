import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.database.db_setup import Base
from backend.src.database.models.user import User
from backend.src.handlers import project_handler
from tests.mock_data.project_data import (
    VALID_PROJECT_NAME, 
    MANAGER_USER, 
    STAFF_USER, 
    VALID_PROJECT, 
    EMPTY_PROJECT_NAME, 
    NOT_FOUND_ID
)
from unittest.mock import patch

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

# INT-077/001
def test_create_and_get_project(isolated_test_db):

    project = project_handler.create_project(VALID_PROJECT_NAME, MANAGER_USER["user_id"])
    assert project["project_name"] == VALID_PROJECT["project_name"]
    assert project["project_manager"] == VALID_PROJECT["project_manager"]
    assert project["active"] == VALID_PROJECT["active"]

    fetched = project_handler.get_project_by_id(VALID_PROJECT["project_id"])
    assert fetched["project_id"] == VALID_PROJECT["project_id"]
    assert fetched["project_name"] == VALID_PROJECT["project_name"]

# INT-077/002
def test_create_project_non_manager_raises(isolated_test_db):

    with pytest.raises(ValueError):
        project_handler.create_project(VALID_PROJECT_NAME, STAFF_USER["user_id"])

# INT-077/003
def test_create_project_empty_name_raises(isolated_test_db):

    with pytest.raises(ValueError):
        project_handler.create_project(EMPTY_PROJECT_NAME, MANAGER_USER["user_id"])

# INT-077/004
def test_get_nonexistent_project(isolated_test_db):

    with pytest.raises(ValueError):
        project_handler.get_project_by_id(NOT_FOUND_ID)

# INT-077/005
def test_get_projects_by_manager_success(isolated_test_db):
    """Test getting all projects managed by a manager."""

    project1 = project_handler.create_project("Project Alpha", MANAGER_USER["user_id"])
    project2 = project_handler.create_project("Project Beta", MANAGER_USER["user_id"])

    manager_projects = project_handler.get_projects_by_manager(MANAGER_USER["user_id"])
    
    assert isinstance(manager_projects, list)
    assert len(manager_projects) == 2
    assert all(p["project_manager"] == MANAGER_USER["user_id"] for p in manager_projects)
    assert project1["project_id"] in [p["project_id"] for p in manager_projects]
    assert project2["project_id"] in [p["project_id"] for p in manager_projects]

# INT-077/006
def test_get_projects_by_manager_no_projects(isolated_test_db):
    """Test getting projects for a manager with no projects."""
    projects = project_handler.get_projects_by_manager(MANAGER_USER["user_id"])
    
    assert isinstance(projects, list)
    assert len(projects) == 0
