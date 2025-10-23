import pytest
import tempfile
import os
from sqlalchemy import create_engine, delete
from unittest.mock import patch
from sqlalchemy.orm import Session, sessionmaker
from backend.src.database.db_setup import Base
from backend.src.services import team as team_service
from backend.src.database.models.team_assignment import TeamAssignment
from backend.src.database.models.user import User
from tests.mock_data.team_data import (
    VALID_TEAM_CREATE,
    STAFF_USER,
    MANAGER_USER,
    NOT_FOUND_ID,
    DIRECTOR_USER,
)


@pytest.fixture(autouse=True)
def clean_db(test_engine):
    """Clean tables BEFORE each test"""
    TestingSession = sessionmaker(bind=test_engine, future=True)
    with TestingSession.begin() as s:
        s.execute(delete(TeamAssignment))
        s.execute(delete(User))
    yield

@pytest.fixture(autouse=True)
def isolated_test_db():

    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    test_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine)

    with patch('backend.src.services.team.SessionLocal', TestSessionLocal):
        yield test_engine
 
    test_engine.dispose()
    try:
        os.unlink(db_path)
    except (OSError, PermissionError):
        pass 

@pytest.fixture(autouse=True)
def seed_task_and_user(test_engine):
    """Insert a user, project, and task to satisfy comment foreign keys."""
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        staff = User(**STAFF_USER)
        manager = User(**MANAGER_USER)
        director = User(**DIRECTOR_USER)
        db.add_all([staff, manager, director]) 

# for subsequent handler level integration with user

# # UNI-058/002
# @patch("backend.src.services.team.SessionLocal")
# def test_create_team_non_manager(mock_session_local):
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
#     user = type("User", (), STAFF_USER)
#     with pytest.raises(ValueError):
#         team_service.create_team(
#             VALID_TEAM_CREATE["team_name"],
#             user,
#             department_id=VALID_TEAM_CREATE.get("department_id"),
#             team_number=VALID_TEAM_CREATE.get("team_number"),
#         )

# # INT-058/002
# def test_create_team_integration_non_manager_raises(isolated_test_db):
#     staff = type("U", (), {"user_id": STAFF_USER["user_id"], "role": STAFF_USER["role"]})()
#     # Non-manager should not be allowed to create a team
#     with pytest.raises(ValueError) as exc:
#         team_service.create_team(
#             VALID_TEAM_CREATE["team_name"],
#             staff,
#             department_id=VALID_TEAM_CREATE.get("department_id"),
#             team_number=VALID_TEAM_CREATE.get("team_number"),
#         )
#     assert "Only managers" in str(exc.value)

# # INT-062/002
# def test_director_can_assign(isolated_test_db):
#     # Create manager-owned team, director assigns
#     manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
#     team = team_service.create_team(
#         VALID_TEAM_CREATE["team_name"], manager,
#         department_id=VALID_TEAM_CREATE.get("department_id"),
#         team_number=VALID_TEAM_CREATE.get("team_number"),
#     )

#     director = type("U", (), {"user_id": DIRECTOR_USER["user_id"], "role": DIRECTOR_USER["role"]})()
#     assignee_id = ASSIGNEE_ID_222
#     result = team_service.assign_to_team(team["team_id"], assignee_id, director)
#     assert result["team_id"] == team["team_id"]
#     assert result["user_id"] == assignee_id


# # UNI-062/002
# @patch("backend.src.services.team.SessionLocal")
# def test_assign_to_team_success_director(mock_session_local):
# 	mock_session = MagicMock()
# 	mock_session_local.begin.return_value.__enter__.return_value = mock_session
# 	mock_team = MagicMock()
# 	mock_team.team_id = TEAM_ID_2
# 	mock_session.get.return_value = mock_team

# 	user = make_user(DIRECTOR_USER)
# 	result = team_service.assign_to_team(TEAM_ID_2, ASSIGNEE_ID_222, user)

# 	assert result["team_id"] == TEAM_ID_2
# 	assert "id" in result
# 	assert result["team_id"] == TEAM_ID_2
# 	assert result["user_id"] == ASSIGNEE_ID_222


# # UNI-062/003
# @pytest.mark.parametrize("user_dict", [STAFF_USER, NO_ROLE_USER])
# @patch("backend.src.services.team.SessionLocal")
# def test_assign_to_team_unauthorized(mock_session_local, user_dict):
# 	mock_session = MagicMock()
# 	mock_session_local.begin.return_value.__enter__.return_value = mock_session
# 	user = make_user(user_dict)
# 	with pytest.raises(ValueError):
# 		team_service.assign_to_team(TEAM_ID_1, ASSIGNEE_ID_55, user)

# # INT-062/003
# def test_unauthorized_user_cannot_assign(isolated_test_db):
#     manager = type("U", (), {"user_id": MANAGER_USER["user_id"], "role": MANAGER_USER["role"]})()
#     team = team_service.create_team(
#         VALID_TEAM_CREATE["team_name"], manager,
#         department_id=VALID_TEAM_CREATE.get("department_id"),
#         team_number=VALID_TEAM_CREATE.get("team_number"),
#     )

#     staff = type("U", (), {"user_id": STAFF_USER["user_id"], "role": STAFF_USER["role"]})()
#     with pytest.raises(ValueError):
#         team_service.assign_to_team(team["team_id"], ASSIGNEE_ID_999, staff)

# # INT-062/005
# def test_assign_with_nonexistent_user_id_raises_error(isolated_test_db):
#     """Assigning an arbitrary (non-existent) user_id should create a TeamAssignment record.

#     The project uses a simple integration DB for tests; we don't create a users row here.
#     The service inserts the assignment row (FK constraints depend on SQLite PRAGMA); assert the row exists.
#     """

#     team = team_service.create_team(VALID_TEAM_CREATE["team_name"], MANAGER_USER["user_id"], department_id=VALID_TEAM_CREATE["department_id"], team_number=VALID_TEAM_CREATE["team_number"])

#     with pytest.raises(ValueError):
#         team_service.assign_to_team(team["team_id"], INVALID_USER_ID, MANAGER_USER["user_id"])