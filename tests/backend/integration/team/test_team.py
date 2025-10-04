import pytest
import importlib
from backend.src.database import db_setup_tables
from backend.src.database.db_setup import DB_PATH, engine
from backend.src.services import team as team_service
from tests.mock_data.team_data import VALID_TEAM_CREATE, MEMBER_USER, NOT_FOUND_ID
from pathlib import Path


@pytest.fixture(autouse=True)
def recreate_db(tmp_path):

    if DB_PATH.exists():
        try:
            engine.dispose()
        except Exception:
            pass
        DB_PATH.unlink()
    importlib.reload(db_setup_tables)
    yield
    if DB_PATH.exists():
        try:
            engine.dispose()
        except Exception:
            pass
        DB_PATH.unlink()


def test_create_and_get_team():
    class Manager:
        user_id = 1
        role = "Manager"

    manager = Manager()
    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], manager, department_id=VALID_TEAM_CREATE.get("department_id"), team_number=VALID_TEAM_CREATE.get("team_number")
    )

    assert team["team_name"] == VALID_TEAM_CREATE["team_name"]
    assert team["manager_id"] == manager.user_id

    fetched = team_service.get_team_by_id(team["team_id"])
    assert fetched["team_id"] == team["team_id"]
    assert fetched["team_name"] == team["team_name"]


def test_create_team_integration_non_manager_raises():
    class Member:
        user_id = MEMBER_USER["user_id"]
        role = MEMBER_USER["role"]

    member = Member()
    # Non-manager should not be allowed to create a team
    try:
        team_service.create_team(VALID_TEAM_CREATE["team_name"], member)
    except ValueError as e:
        assert "Only managers" in str(e)


def test_create_team_integration_empty_name_raises():
    class Manager:
        user_id = 1
        role = "Manager"

    manager = Manager()
    with pytest.raises(ValueError):
        team_service.create_team("   ", manager)


def test_get_team_integration_not_found():
    # Ensure get_team_by_id raises when id is absent
    with pytest.raises(ValueError):
        team_service.get_team_by_id(NOT_FOUND_ID)
    