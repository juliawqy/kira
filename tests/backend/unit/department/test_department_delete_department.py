import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.department_data import VALID_DEPARTMENT_ID, INVALID_DEPARTMENT_ID

# KIRA-002/014
@patch("backend.src.services.department.SessionLocal")
def test_delete_department_success(mock_session_local, mock_session):
    from backend.src.services import department as dept_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    mock_dept = MagicMock(id=VALID_DEPARTMENT_ID)
    mock_dept.subdepartments = [MagicMock(id=2), MagicMock(id=3)]
    mock_session.get.return_value = mock_dept

    result = dept_service.delete_department(VALID_DEPARTMENT_ID)
    assert result == {"deleted": VALID_DEPARTMENT_ID, "subdepartments_detached": 2}
    mock_session.delete.assert_called_once_with(mock_dept)


# KIRA-002/015
@patch("backend.src.services.department.SessionLocal")
def test_delete_department_not_found(mock_session_local, mock_session):
    from backend.src.services import department as dept_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    with pytest.raises(ValueError, match="Department id"):
        dept_service.delete_department(INVALID_DEPARTMENT_ID)
