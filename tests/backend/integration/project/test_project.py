import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.database.db_setup import Base
from backend.src.services import project as project_service
from tests.mock_data.project_data import VALID_PROJECT_NAME, MANAGER_USER, STAFF_USER, NOT_FOUND_ID
from unittest.mock import patch

@pytest.fixture(autouse=True)
def isolated_test_db():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    test_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine)

    with patch('backend.src.services.project.SessionLocal', TestSessionLocal):
        yield test_engine

    test_engine.dispose()
    try:
        os.unlink(db_path)
    except (OSError, PermissionError):
        pass

# INT-083/001
def test_create_and_get_project(isolated_test_db):
    user = type("User", (), MANAGER_USER)()
    project = project_service.create_project(VALID_PROJECT_NAME, user)
    assert project["project_name"] == VALID_PROJECT_NAME
    assert project["project_manager"] == user.user_id
    assert project["active"] is True

    fetched = project_service.get_project_by_id(project["project_id"])
    assert fetched["project_id"] == project["project_id"]
    assert fetched["project_name"] == project["project_name"]

# INT-083/002
def test_create_project_non_manager_raises(isolated_test_db):
    user = type("User", (), STAFF_USER)()
    with pytest.raises(ValueError):
        project_service.create_project(VALID_PROJECT_NAME, user)

# INT-083/003
def test_create_project_empty_name_raises(isolated_test_db):
    user = type("User", (), MANAGER_USER)()
    with pytest.raises(ValueError):
        project_service.create_project("   ", user)

# INT-083/004
def test_get_project_not_found_raises(isolated_test_db):
    with pytest.raises(ValueError):
        project_service.get_project_by_id(NOT_FOUND_ID)
