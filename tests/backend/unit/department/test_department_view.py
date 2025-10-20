# tests/backend/unit/department/test_department_view.py
import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import department as dept_service
from tests.mock_data.department_data import (
    VALID_DEPARTMENT_1,
    VALID_DEPARTMENT_ID,
    INVALID_DEPARTMENT_ID,
)

# UNI-069/001
@patch("backend.src.services.department.SessionLocal")
def test_get_department_by_id_success(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session
    mock_dept = MagicMock()
    mock_dept.department_id = VALID_DEPARTMENT_1["department_id"]
    mock_dept.department_name = VALID_DEPARTMENT_1["department_name"]
    mock_dept.manager_id = VALID_DEPARTMENT_1["manager_id"]
    mock_session.query.return_value.filter.return_value.first.return_value = mock_dept

    result = dept_service.get_department_by_id(VALID_DEPARTMENT_ID)

    assert isinstance(result, dict)
    assert result["department_id"] == VALID_DEPARTMENT_1["department_id"]
    assert result["department_name"] == VALID_DEPARTMENT_1["department_name"]
    assert result["manager_id"] == VALID_DEPARTMENT_1["manager_id"]

# UNI-069/002
@patch("backend.src.services.department.SessionLocal")
def test_get_department_by_id_not_found(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_session.query.return_value.filter.return_value.first.return_value = None

    result = dept_service.get_department_by_id(INVALID_DEPARTMENT_ID)
    assert result is None
