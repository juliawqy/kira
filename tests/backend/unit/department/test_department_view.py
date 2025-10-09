
from unittest.mock import patch, MagicMock
from tests.mock_data.department_data import VALID_DEPARTMENT_1

@patch("backend.src.services.department.SessionLocal")
def test_get_department_by_id(mock_session_local):
    from backend.src.services import department as dept_service

    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    # Use mock data from department_data.py
    mock_department = MagicMock()
    mock_department.id = VALID_DEPARTMENT_1["id"]
    mock_department.name = VALID_DEPARTMENT_1["name"]
    mock_department.main = VALID_DEPARTMENT_1.get("main", None)
    mock_department.manager_id = VALID_DEPARTMENT_1.get("manager_id", None)

    mock_session.query.return_value.filter.return_value.first.return_value = mock_department

    result = dept_service.get_department_by_id(VALID_DEPARTMENT_1["id"])

    assert result["id"] == VALID_DEPARTMENT_1["id"]
    assert result["name"] == VALID_DEPARTMENT_1["name"]