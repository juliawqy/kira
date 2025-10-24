import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import project as project_service
from tests.mock_data.project_data import MANAGER_USER, STAFF_USER, NOT_FOUND_ID, VALID_PROJECT

# UNI-081/001
@patch("backend.src.services.project.SessionLocal")
def test_assign_user_to_project_success(mock_session_local):
    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    result = project_service.assign_user_to_project(
        VALID_PROJECT["project_id"], STAFF_USER["user_id"]
    )

    assert result["project_id"] == VALID_PROJECT["project_id"]
    assert result["user_id"] == STAFF_USER["user_id"]
    mock_session.add.assert_called_once()

# UNI-081/002
@patch("backend.src.services.project.SessionLocal")
def test_duplicate_assignment_raises(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
    with pytest.raises(ValueError, match="already assigned"):
        project_service.assign_user_to_project(VALID_PROJECT["project_id"], STAFF_USER["user_id"])
