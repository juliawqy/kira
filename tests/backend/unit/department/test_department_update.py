import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.department_data import VALID_DEPARTMENT_1, VALID_DEPARTMENT_ID, INVALID_DEPARTMENT_ID

# KIRA-002/005
@patch("backend.src.services.department.SessionLocal")
def test_update_department_success(mock_session_local, mock_session):
    from backend.src.services import department as dept_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_dept = MagicMock(**VALID_DEPARTMENT_1)
    mock_session.get.return_value = mock_dept

    updated = dept_service.update_department(VALID_DEPARTMENT_ID, name="New Dept Name")

    assert updated.name == "New Dept Name"
    mock_session.add.assert_called_once_with(mock_dept)


# KIRA-002/006
@patch("backend.src.services.department.SessionLocal")
def test_update_department_not_found(mock_session_local, mock_session):
    from backend.src.services import department as dept_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    result = dept_service.update_department(INVALID_DEPARTMENT_ID, name="Ghost Dept")
    assert result is None
    