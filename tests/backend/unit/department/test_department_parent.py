import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.department_data import VALID_DEPARTMENT_1, VALID_DEPARTMENT_2

# KIRA-002/004
@patch("backend.src.services.department.SessionLocal")
def test_list_parent_departments(mock_session_local, mock_session):
    from backend.src.services import department as dept_service

    mock_session_local.return_value.__enter__.return_value = mock_session

    mock_dept1 = MagicMock(**VALID_DEPARTMENT_1)
    mock_dept2 = MagicMock(**VALID_DEPARTMENT_2)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_dept1, mock_dept2]
    mock_session.execute.return_value = mock_result

    result = dept_service.list_parent_departments()

    assert len(result) == 2
    assert result[0].name == VALID_DEPARTMENT_1["name"]
    assert result[1].name == VALID_DEPARTMENT_2["name"]
