import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import project as project_service
from tests.mock_data.project_data import VALID_PROJECT_NAME, MANAGER_USER, NOT_FOUND_ID, TEST_PROJECT_ID


def make_user(user_dict):
    return type("User", (), user_dict)

# UNI-078/001
@patch("backend.src.services.project.SessionLocal")
def test_view_project_success(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_project = MagicMock()
    mock_project.project_id = TEST_PROJECT_ID
    mock_project.project_name = VALID_PROJECT_NAME
    mock_project.project_manager = MANAGER_USER["user_id"]
    mock_project.active = True

    mock_session.get.return_value = mock_project

    result = project_service.get_project_by_id(TEST_PROJECT_ID)
    assert result["project_id"] == TEST_PROJECT_ID
    assert result["project_name"] == VALID_PROJECT_NAME
    assert result["project_manager"] == MANAGER_USER["user_id"]
    assert result["active"] is True

# # UNI-078/002
@patch("backend.src.services.project.SessionLocal")
def test_view_project_not_found(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_session.get.return_value = None

    result = project_service.get_project_by_id(NOT_FOUND_ID)
    assert result is None