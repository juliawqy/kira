import pytest
from unittest.mock import patch, MagicMock
from backend.src.services import department as dept_service

@patch("backend.src.services.department.SessionLocal")
def test_create_department_permission_error(mock_session_local):
    with pytest.raises(PermissionError):
        dept_service.create_department(name="Engineering", manager="Alice Tan", user_role="Staff")

@patch("backend.src.services.department.SessionLocal")
def test_create_department_db_exception(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session
    mock_session.add.side_effect = Exception("DB error!")
    with pytest.raises(Exception) as excinfo:
        dept_service.create_department(name="Engineering", manager="Alice Tan")
    assert "DB error!" in str(excinfo.value)

@patch("backend.src.services.department.SessionLocal")
def test_get_department_by_id_exception(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.side_effect = Exception("Query error!")
    with pytest.raises(Exception) as excinfo:
        dept_service.get_department_by_id(1)
    assert "Query error!" in str(excinfo.value)

@patch("backend.src.services.department.SessionLocal")
def test_get_department_by_id_none(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = None
    result = dept_service.get_department_by_id(999)
    assert result is None
