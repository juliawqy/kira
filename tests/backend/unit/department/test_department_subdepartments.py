import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.department_data import VALID_DEPARTMENT_1, VALID_DEPARTMENT_ID

# KIRA-002/003
@patch("backend.src.services.department.SessionLocal")
def test_get_department_with_subdepartments(mock_session_local, mock_session):
    from backend.src.services import department as dept_service

    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_department = MagicMock()
    mock_department.id = VALID_DEPARTMENT_1["id"]
    mock_department.name = VALID_DEPARTMENT_1["name"]
    mock_department.subdepartments = [MagicMock(id=2, name="SubDept A")]

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_department
    mock_session.execute.return_value = mock_result

    result = dept_service.get_department_with_subdepartments(VALID_DEPARTMENT_ID)

    assert result.id == VALID_DEPARTMENT_1["id"]
    assert result.name == VALID_DEPARTMENT_1["name"]
    assert len(result.subdepartments) == 1
