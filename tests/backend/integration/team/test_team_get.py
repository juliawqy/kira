import pytest
import tempfile
import os
from sqlalchemy import create_engine, delete
from unittest.mock import patch
from sqlalchemy.orm import sessionmaker
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
    VALID_TEAM
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
    

# INT-061/001
def test_get_team():
    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], 
        VALID_TEAM_CREATE["manager_id"], 
        department_id=VALID_TEAM_CREATE["department_id"], 
        prefix=str(VALID_TEAM_CREATE["department_id"])
    )

    fetched = team_service.get_team_by_id(VALID_TEAM["team_id"])
    assert fetched["team_id"] == VALID_TEAM["team_id"]
    assert fetched["team_name"] == VALID_TEAM["team_name"]

# INT-061/002
def test_get_team_nonexistent():
    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], 
        VALID_TEAM_CREATE["manager_id"], 
        department_id=VALID_TEAM_CREATE["department_id"], 
        prefix=str(VALID_TEAM_CREATE["department_id"])
    )
    
    with pytest.raises(ValueError):
        team_service.get_team_by_id(NOT_FOUND_ID)

