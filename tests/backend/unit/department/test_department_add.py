# tests/backend/unit/department/test_department_add.py
import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import department as dept_service
from tests.mock_data.department_data import (
    SERVICE_ADD_DEPARTMENT,
    VALID_DEPARTMENT_1,
)

# UNI-067/001
@patch("backend.src.services.department.SessionLocal")
def test_add_department_success(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session
    dept = dept_service.add_department(**SERVICE_ADD_DEPARTMENT)
    assert dept["department_name"] == VALID_DEPARTMENT_1["department_name"]
    assert dept["manager_id"] == VALID_DEPARTMENT_1["manager_id"]


