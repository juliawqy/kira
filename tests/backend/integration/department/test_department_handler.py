import pytest
import importlib
import tempfile
import os
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch
from backend.src.database.db_setup import Base
from backend.src.handlers import department_handler
from backend.src.services import team as team_service
from backend.src.services import user as user_service
from backend.src.database.models.user import User
from backend.src.database.models.team import Team
from backend.src.database.models.department import Department
from backend.src.database.models.team_assignment import TeamAssignment
from tests.mock_data.team_data import (
    STAFF_USER, 
    MANAGER_USER, 
    DIRECTOR_USER,
    HR_USER,
    VALID_TEAM_CREATE, 
    VALID_TEAM, 
    VALID_SUBTEAM_CREATE, 
    VALID_SUBTEAM, 
    NOT_FOUND_ID,
    INVALID_TEAM_NUMBER
)
from tests.mock_data.department_data import (
    VALID_DEPARTMENT_1, 
    INVALID_DEPARTMENT_ID,
    VALID_ADD_DEPARTMENT,
    VALID_DEPARTMENT_2,
    INVALID_DEPARTMENT_NO_NAME,
    INVALID_DEPARTMENT_NO_MANAGER,
    INVALID_DEPARTMENT_NON_HR
)
from tests.mock_data.user.integration_data import (
    VALID_USER_ADMIN,
    VALID_USER,
    VALID_CREATE_PAYLOAD_USER,
    INVALID_USER_ID,
)


@pytest.fixture(autouse=True)
def clean_db(test_engine):
    """Clean tables BEFORE each test"""
    TestingSession = sessionmaker(bind=test_engine, future=True)
    with TestingSession.begin() as s:
        s.execute(delete(TeamAssignment))
        s.execute(delete(Team))
        s.execute(delete(Department))
        s.execute(delete(User))
    yield


@pytest.fixture
def isolated_test_db():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    test_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine)

    with patch('backend.src.services.team.SessionLocal', TestSessionLocal), \
         patch('backend.src.services.department.SessionLocal', TestSessionLocal), \
         patch('backend.src.services.user.SessionLocal', TestSessionLocal), \
         patch('backend.src.handlers.department_handler.department_service.SessionLocal', TestSessionLocal), \
         patch('backend.src.handlers.department_handler.team_service.SessionLocal', TestSessionLocal), \
         patch('backend.src.handlers.department_handler.user_service.SessionLocal', TestSessionLocal):

        department_handler = importlib.import_module("backend.src.handlers.department_handler")
        yield test_engine, team_service, department_handler

    test_engine.dispose()
    try:
        os.unlink(db_path)
    except (OSError, PermissionError):
        pass


@pytest.fixture(autouse=True)
def seed_users_and_department(isolated_test_db):
    test_engine, _, _ = isolated_test_db
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        staff = User(**{**STAFF_USER, "department_id": None})
        manager = User(**{**MANAGER_USER, "department_id": None})
        director = User(**{**DIRECTOR_USER, "department_id": None})
        hr = User(**{**HR_USER, "department_id": None})
        db.add_all([staff, manager, director, hr])
        db.flush() 
        dept_payload = {**VALID_DEPARTMENT_1, "manager_id": manager.user_id}
        dept = Department(**dept_payload)
        db.add(dept)
        db.flush()
        staff.department_id = dept.department_id
        manager.department_id = dept.department_id
        director.department_id = dept.department_id
        db.add_all([staff, manager, director])



# INT-104/001
def test_view_team_by_department(isolated_test_db):

    department_handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"],
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    teams = department_handler.view_teams_in_department(VALID_DEPARTMENT_1["department_id"])
    assert isinstance(teams, list)
    assert len(teams) == 1
    assert teams[0]["team_name"] == VALID_TEAM_CREATE["team_name"]


# INT-104/002
def test_view_team_by_nonexistent_department(isolated_test_db):
    with pytest.raises(ValueError):
        department_handler.view_teams_in_department(INVALID_DEPARTMENT_ID)

# INT-104/003
def test_view_subteam_by_team(isolated_test_db):

    department_handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"],
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    department_handler.create_team_under_team(
        VALID_SUBTEAM_CREATE["team_id"],
        VALID_SUBTEAM_CREATE["team_name"],
        VALID_SUBTEAM_CREATE["manager_id"]
    )

    subteams = department_handler.view_subteams_in_team(VALID_TEAM["team_id"])

    assert isinstance(subteams, list)
    assert len(subteams) == 1
    assert subteams[0]["team_name"] == VALID_SUBTEAM["team_name"]
    assert subteams[0]["manager_id"] == VALID_SUBTEAM["manager_id"]
    assert subteams[0]["department_id"] == VALID_SUBTEAM["department_id"]
    assert subteams[0]["team_number"] == VALID_SUBTEAM["team_number"]


# INT-104/004
def test_view_subteam_by_invalid_team(isolated_test_db):

    with pytest.raises(ValueError):
        department_handler.view_subteams_in_team(INVALID_TEAM_NUMBER)


# INT-104/005
def test_view_team_by_department_empty(isolated_test_db):

    teams = department_handler.view_teams_in_department(VALID_DEPARTMENT_1["department_id"])
    assert teams == []


# INT-104/006
def test_view_team_by_team_empty(isolated_test_db):

    department_handler.create_team_under_department(
        VALID_TEAM_CREATE["department_id"],
        VALID_TEAM_CREATE["team_name"],
        VALID_TEAM_CREATE["manager_id"]
    )

    subteams = department_handler.view_subteams_in_team(VALID_TEAM["team_id"])
    assert subteams == []


# INT-125/001
def test_view_users_in_department_returns_mapped_users(isolated_test_db):
    users = department_handler.view_users_in_department(VALID_DEPARTMENT_1["department_id"])
    assert isinstance(users, list)
    assert len(users) == 3

    user = users[0]
    assert user["user_id"] == STAFF_USER["user_id"]
    assert user["name"] == STAFF_USER["name"]
    assert user["email"] == STAFF_USER["email"]
    assert user["role"] == STAFF_USER["role"]
    assert user["admin"] == STAFF_USER["admin"]

# INT-125/002
def test_view_users_in_nonexistent_department_raises(isolated_test_db):
    with pytest.raises(ValueError) as e:
        department_handler.view_users_in_department(INVALID_DEPARTMENT_ID)
    assert f"Department {INVALID_DEPARTMENT_ID} not found" in str(e.value)  


# INT-125/003
def test_assign_user_to_department_success(isolated_test_db):
    user_id = STAFF_USER["user_id"]
    dept_id = VALID_DEPARTMENT_1["department_id"]
    user_service.assign_user_to_department(user_id, dept_id)
    users = department_handler.view_users_in_department(dept_id)

    assert user_id in [user["user_id"] for user in users]


# INT-125/004
def test_assign_user_to_department_user_not_found_raises(isolated_test_db):
    with pytest.raises(ValueError) as e:
        user_service.assign_user_to_department(INVALID_USER_ID, VALID_DEPARTMENT_1["department_id"])
    assert f"User {INVALID_USER_ID} not found" in str(e.value)


# INT-125/005
def test_assign_user_to_department_department_not_found_raises(isolated_test_db):
    user_id = STAFF_USER["user_id"]
    with pytest.raises(ValueError) as e:
        user_service.assign_user_to_department(user_id, INVALID_DEPARTMENT_ID)
    assert f"Department {INVALID_DEPARTMENT_ID} not found" in str(e.value)


# INT-125/006
def test_unassign_user_from_department_success(isolated_test_db):
    user_id = STAFF_USER["user_id"]
    dept_id = VALID_DEPARTMENT_1["department_id"]
    user_service.assign_user_to_department(user_id, dept_id)
    user_service.assign_user_to_department(user_id, None)
    users = department_handler.view_users_in_department(dept_id)

    assert user_id not in [user["user_id"] for user in users]

# INT-125/007
def test_route_list_users_in_department(isolated_test_db):
    from backend.src.api.v1.routes.user_route import list_users_in_department
    dept_id = VALID_DEPARTMENT_1["department_id"]
    models = list_users_in_department(dept_id)
    assert isinstance(models, list)
    assert len(models) >= 1
    u0 = models[0]
    assert hasattr(u0, "user_id")
    assert hasattr(u0, "name")
    assert hasattr(u0, "email")
    assert hasattr(u0, "role")
    assert hasattr(u0, "admin")

# INT-067/001
def test_create_department(isolated_test_db):
    dept = department_handler.add_department(
        VALID_ADD_DEPARTMENT["department_name"],
        VALID_ADD_DEPARTMENT["manager_id"],
        VALID_ADD_DEPARTMENT["creator_id"]
    )

    assert dept["department_name"] == VALID_DEPARTMENT_2["department_name"]
    assert dept["manager_id"] == VALID_DEPARTMENT_2["manager_id"]
    assert dept["department_id"] == VALID_DEPARTMENT_2["department_id"]

# INT-067/002
@pytest.mark.parametrize("invalid_payload", [INVALID_DEPARTMENT_NO_NAME, INVALID_DEPARTMENT_NO_MANAGER])
def test_create_department_validation_errors(isolated_test_db, invalid_payload):
    with pytest.raises(ValueError):
        department_handler.add_department(
            invalid_payload["department_name"],
            invalid_payload["manager_id"],
            invalid_payload["creator_id"]
        )
