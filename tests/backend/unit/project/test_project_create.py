import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import project as project_service
from tests.mock_data.project_data import VALID_PROJECT_NAME, MANAGER_USER, STAFF_USER

# UNI-083/001
@patch("backend.src.services.project.SessionLocal")
def test_create_project_success(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    user = type("User", (), MANAGER_USER)
    project = project_service.create_project(VALID_PROJECT_NAME, user)

    assert project["project_name"] == VALID_PROJECT_NAME
    assert project["project_manager"] == MANAGER_USER["user_id"]
    assert project["active"] is True

# UNI-083/002
@patch("backend.src.services.project.SessionLocal")
def test_create_project_non_manager(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    user = type("User", (), STAFF_USER)
    with pytest.raises(ValueError):
        project_service.create_project(VALID_PROJECT_NAME, user)

# UNI-083/003
@patch("backend.src.services.project.SessionLocal")
def test_create_project_blank_name(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    user = type("User", (), MANAGER_USER)
    with pytest.raises(ValueError):
        project_service.create_project("   ", user)

# UNI-083/004
@patch("backend.src.services.project.SessionLocal")
def test_create_project_missing_role(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    user = type("User", (), {"user_id": 42})
    with pytest.raises(ValueError):
        project_service.create_project(VALID_PROJECT_NAME, user)
