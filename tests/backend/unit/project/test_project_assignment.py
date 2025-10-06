import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import project as project_service
from tests.mock_data.project_data import MANAGER_USER, ASSIGNABLE_USER, DUPLICATE_USER, NOT_FOUND_ID, TEST_PROJECT_ID

# UNI-081/001
@patch("backend.src.services.project.SessionLocal")
def test_assign_user_to_project_success(mock_session_local):
    mock_session = MagicMock()
    def get_side_effect(model, id):
        if id == TEST_PROJECT_ID:  
            return MagicMock()  
        if id == ASSIGNABLE_USER["user_id"]:  
            return MagicMock()  
        return None

    mock_session.get.side_effect = get_side_effect
    mock_session.query().filter_by().first.return_value = None  

    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    result = project_service.assign_user_to_project(TEST_PROJECT_ID, ASSIGNABLE_USER["user_id"])
    assert result["project_id"] == TEST_PROJECT_ID
    assert result["user_id"] == ASSIGNABLE_USER["user_id"]

# UNI-081/002
@patch("backend.src.services.project.SessionLocal")
def test_assign_user_to_nonexistent_project(mock_session_local):
    mock_session = MagicMock()
    mock_session.get.side_effect = lambda model, id: None if id == NOT_FOUND_ID else MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    with pytest.raises(ValueError, match="Project not found"):
        project_service.assign_user_to_project(NOT_FOUND_ID, ASSIGNABLE_USER["user_id"])

# UNI-081/003
@patch("backend.src.services.project.SessionLocal")
def test_assign_nonexistent_user_to_project(mock_session_local):
    mock_session = MagicMock()
    mock_session.get.side_effect = lambda model, id: None if id == NOT_FOUND_ID else MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    with pytest.raises(ValueError, match="User not found"):
        project_service.assign_user_to_project(TEST_PROJECT_ID, NOT_FOUND_ID)

# UNI-081/004
@patch("backend.src.services.project.SessionLocal")
def test_duplicate_assignment_raises(mock_session_local):
    mock_session = MagicMock()
    mock_session.get.side_effect = lambda model, id: MagicMock()  
    mock_session.query().filter_by().first.return_value = MagicMock()  

    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    with pytest.raises(ValueError, match="already assigned"):
        project_service.assign_user_to_project(TEST_PROJECT_ID, DUPLICATE_USER["user_id"])
