import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.department_data import VALID_DEPARTMENT_ID, INVALID_DEPARTMENT_ID

# KIRA-002/011
@patch("backend.src.services.department.SessionLocal")
def test_delete_subdepartment_success(mock_session_local, mock_session):
    from backend.src.services import department as dept_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_subdept = MagicMock(id=VALID_DEPARTMENT_ID, parent_id=10)
    mock_session.get.return_value = mock_subdept

    result = dept_service.delete_subdepartment(VALID_DEPARTMENT_ID)
    assert result is True
    mock_session.delete.assert_called_once_with(mock_subdept)


# KIRA-002/012
@patch("backend.src.services.department.SessionLocal")
def test_delete_subdepartment_not_found(mock_session_local, mock_session):
    from backend.src.services import department as dept_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    result = dept_service.delete_subdepartment(INVALID_DEPARTMENT_ID)
    assert result is False


# KIRA-002/013
@patch("backend.src.services.department.SessionLocal")
def test_delete_subdepartment_invalid(mock_session_local, mock_session):
    from backend.src.services import department as dept_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_subdept = MagicMock(id=VALID_DEPARTMENT_ID, parent_id=None)
    mock_session.get.return_value = mock_subdept

    with pytest.raises(ValueError, match="is not a subdepartment"):
        dept_service.delete_subdepartment(VALID_DEPARTMENT_ID)
