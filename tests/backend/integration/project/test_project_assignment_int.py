import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.database.db_setup import Base
from backend.src.services import project as project_service
from backend.src.database.models.user import User
from tests.mock_data.project_data import (
    VALID_PROJECT_NAME,
    MANAGER_USER,
    ASSIGNABLE_USER,
    DUPLICATE_USER,
    NOT_FOUND_ID,
)
from unittest.mock import patch

@pytest.fixture(autouse=True)
def isolated_test_db():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    test_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine)

    # Insert test users
    with TestSessionLocal.begin() as session:
        for user_data in [MANAGER_USER, ASSIGNABLE_USER, DUPLICATE_USER]:
            session.add(User(
                user_id=user_data["user_id"],
                name=f"User{user_data['user_id']}",
                email=user_data["email"],
                role=user_data["role"],
                hashed_pw=user_data["hashed_pw"]
            ))

    with patch("backend.src.services.project.SessionLocal", TestSessionLocal):
        yield test_engine

    test_engine.dispose()
    os.unlink(db_path)


# INT-081/001
def test_assign_user_to_project_success(isolated_test_db):
    manager = type("User", (), MANAGER_USER)()
    project = project_service.create_project(VALID_PROJECT_NAME, manager)
    result = project_service.assign_user_to_project(project["project_id"], ASSIGNABLE_USER["user_id"])

    assert result["project_id"] == project["project_id"]
    assert result["user_id"] == ASSIGNABLE_USER["user_id"]

# INT-081/002
def test_duplicate_assignment_fails(isolated_test_db):
    manager = type("User", (), MANAGER_USER)()
    project = project_service.create_project(VALID_PROJECT_NAME, manager)
    project_service.assign_user_to_project(project["project_id"], DUPLICATE_USER["user_id"])

    with pytest.raises(ValueError, match="already assigned"):
        project_service.assign_user_to_project(project["project_id"], DUPLICATE_USER["user_id"])

# INT-081/003
def test_assign_to_nonexistent_project_fails(isolated_test_db):
    with pytest.raises(ValueError, match="Project not found"):
        project_service.assign_user_to_project(NOT_FOUND_ID, ASSIGNABLE_USER["user_id"])

# INT-081/004
def test_assign_nonexistent_user_fails(isolated_test_db):
    manager = type("User", (), MANAGER_USER)()
    project = project_service.create_project(VALID_PROJECT_NAME, manager)

    with pytest.raises(ValueError, match="User not found"):
        project_service.assign_user_to_project(project["project_id"], NOT_FOUND_ID)
