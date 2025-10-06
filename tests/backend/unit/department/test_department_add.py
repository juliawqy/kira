import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.department_data import (
    VALID_ADD_DEPARTMENT,
    VALID_DEPARTMENT_1,
    INVALID_DEPARTMENT_NO_NAME,
    INVALID_DEPARTMENT_NO_MANAGER,
)

# KIRA-002/001 (test case id corresponding to test case sheets)
@patch("backend.src.services.department.SessionLocal")
def test_add_department_success(mock_session_local, mock_session):
    from backend.src.services import department as dept_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session

    # Create mock Department with ID = 1 (simulating DB auto-generation)
    mock_dept = MagicMock()
    mock_dept.id = VALID_DEPARTMENT_1["id"]
    mock_dept.name = VALID_DEPARTMENT_1["name"]
    mock_dept.description = VALID_DEPARTMENT_1["description"]
    mock_dept.manager = VALID_DEPARTMENT_1["manager"]
    mock_dept.created_at = VALID_DEPARTMENT_1["created_at"]

    with patch("backend.src.services.department.Department", return_value=mock_dept):
        result = dept_service.add_department(**VALID_ADD_DEPARTMENT)
        assert result.id == VALID_DEPARTMENT_1["id"]
        assert result.name == VALID_DEPARTMENT_1["name"]
        assert result.manager == VALID_DEPARTMENT_1["manager"]


@pytest.mark.parametrize("invalid_department", [
    INVALID_DEPARTMENT_NO_NAME,
    INVALID_DEPARTMENT_NO_MANAGER,
])
# KIRA-002/002 (test case id corresponding to test case sheets)
@patch("backend.src.services.department.SessionLocal")
def test_add_department_failure(mock_session_local, mock_session, invalid_department):
    from backend.src.services import department as dept_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    with pytest.raises(ValueError):
        dept_service.add_department(**invalid_department)
