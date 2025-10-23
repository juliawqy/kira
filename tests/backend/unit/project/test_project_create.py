import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import project as project_service
from tests.mock_data.project_data import VALID_PROJECT_NAME, MANAGER_USER, STAFF_USER, EMPTY_PROJECT_NAME, MISSING_ROLE_USER, VALID_PROJECT

# UNI-077/001
@patch("backend.src.services.project.SessionLocal")
def test_create_project_success(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    project = project_service.create_project(VALID_PROJECT_NAME, MANAGER_USER["user_id"])

    assert project["project_name"] == VALID_PROJECT["project_name"]
    assert project["project_manager"] == VALID_PROJECT["project_manager"]
    assert project["active"] == VALID_PROJECT["active"]
