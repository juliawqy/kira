import pytest
from unittest.mock import patch, MagicMock
from tests.mock_data.department_data import VALID_DEPARTMENT_ID, INVALID_DEPARTMENT_ID

# KIRA-002/009
@patch("backend.src.services.department.SessionLocal")
def test_unassign_members_success(mock_session_local, mock_session):
    from backend.src.services import department as dept_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_dept = MagicMock()
    mock_dept.members = "Alice,Bob,Charlie"
    mock_session.get.return_value = mock_dept

    with patch("backend.src.services.department._csv_to_list", return_value=["Alice", "Bob", "Charlie"]), \
         patch("backend.src.services.department._normalize_members", return_value=["Charlie"]), \
         patch("backend.src.services.department._list_to_csv", return_value="Charlie"):

        result = dept_service.unassign_members(VALID_DEPARTMENT_ID, ["Alice", "Bob"])
        assert result.members == "Charlie"


# KIRA-002/010
@patch("backend.src.services.department.SessionLocal")
def test_unassign_members_not_found(mock_session_local, mock_session):
    from backend.src.services import department as dept_service

    mock_session_local.begin.return_value.__enter__.return_value = mock_session
    mock_session.get.return_value = None

    with pytest.raises(ValueError, match="Department not found"):
        dept_service.unassign_members(INVALID_DEPARTMENT_ID, ["Zoe"])
