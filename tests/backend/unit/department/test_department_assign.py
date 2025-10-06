import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.department_data import VALID_DEPARTMENT_ID, INVALID_DEPARTMENT_ID

# KIRA-002/007
@patch("backend.src.services.department.SessionLocal")
def test_assign_members_success(mock_session_local, mock_session):
    from backend.src.services import department as dept_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_dept = MagicMock()
    mock_dept.members = "Alice,Bob"
    mock_session.get.return_value = mock_dept

    with patch("backend.src.services.department._csv_to_list", return_value=["Alice", "Bob"]), \
         patch("backend.src.services.department._normalize_members", return_value=["Alice", "Bob", "Charlie"]), \
         patch("backend.src.services.department._list_to_csv", return_value="Alice,Bob,Charlie"):

        result = dept_service.assign_members(VALID_DEPARTMENT_ID, ["Charlie"])
        assert result.members == "Alice,Bob,Charlie"


# KIRA-002/008
@patch("backend.src.services.department.SessionLocal")
def test_assign_members_not_found(mock_session_local, mock_session):
    from backend.src.services import department as dept_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    with pytest.raises(ValueError, match="Department not found"):
        dept_service.assign_members(INVALID_DEPARTMENT_ID, ["Zoe"])
