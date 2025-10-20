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

# KIRA-002/001 — success (HR creates department)
@patch("backend.src.services.department.SessionLocal")
def test_add_department_success(mock_session_local):
    # Make SessionLocal() return a mock session object
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    # Call service
    dept = dept_service.add_department(**VALID_ADD_DEPARTMENT)

    # Assert returned ORM object fields (we don't assert department_id since no real DB flush)
    assert getattr(dept, "department_name", None) == VALID_DEPARTMENT_1["department_name"]
    assert getattr(dept, "manager_id", None) == VALID_DEPARTMENT_1["manager_id"]


# KIRA-002/002 — validation failures (HR role present but bad inputs)
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
    # No DB interaction assertions (kept consistent with team tests)


# KIRA-002/003 — permission failure (non-HR cannot create)
@patch("backend.src.services.department.SessionLocal")
def test_add_department_permission_denied(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    with pytest.raises(PermissionError):
        dept_service.add_department(**INVALID_DEPARTMENT_NON_HR)
    # Same style: no DB interaction assertions

@patch("backend.src.services.department.SessionLocal")
def test_add_department_db_error_triggers_rollback(mock_session_local):
    # Mock the context-managed session
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    # Force an error inside the try: block
    mock_session.add.side_effect = RuntimeError("insert failed")

    with pytest.raises(RuntimeError):
        dept_service.add_department(**VALID_ADD_DEPARTMENT)

    # Ensure we hit the except: path
    mock_session.rollback.assert_called_once()
    mock_session.commit.assert_not_called()
