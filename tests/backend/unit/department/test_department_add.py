# tests/backend/unit/department/test_department_add.py
import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import department as dept_service
from tests.mock_data.department_data import (
    VALID_ADD_DEPARTMENT,
    VALID_DEPARTMENT_1,
    INVALID_DEPARTMENT_NO_NAME,
    INVALID_DEPARTMENT_NO_MANAGER,
    INVALID_DEPARTMENT_NON_HR,
)

# UNI-067/001
@patch("backend.src.services.department.SessionLocal")
def test_add_department_success(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session
    dept = dept_service.add_department(**VALID_ADD_DEPARTMENT)
    assert getattr(dept, "department_name", None) == VALID_DEPARTMENT_1["department_name"]
    assert getattr(dept, "manager_id", None) == VALID_DEPARTMENT_1["manager_id"]


# UNI-067/002
@pytest.mark.parametrize("invalid_payload", [
    INVALID_DEPARTMENT_NO_NAME,
    INVALID_DEPARTMENT_NO_MANAGER,
])

@patch("backend.src.services.department.SessionLocal")
def test_add_department_failure_validation(mock_session_local, invalid_payload):
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    with pytest.raises(ValueError):
        dept_service.add_department(**invalid_payload)


# UNI-067/003
@patch("backend.src.services.department.SessionLocal")
def test_add_department_permission_denied(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    with pytest.raises(PermissionError):
        dept_service.add_department(**INVALID_DEPARTMENT_NON_HR)

# UNI-067/004
@patch("backend.src.services.department.SessionLocal")
def test_add_department_db_error_triggers_rollback(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_session.add.side_effect = RuntimeError("insert failed")
    with pytest.raises(RuntimeError):
        dept_service.add_department(**VALID_ADD_DEPARTMENT)
    mock_session.rollback.assert_called_once()
    mock_session.commit.assert_not_called()
