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


# INT-062/001
def test_assign_to_team_not_found():
    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], MANAGER_USER["user_id"],
        department_id=VALID_TEAM_CREATE["department_id"],
        team_number=VALID_TEAM_CREATE["team_number"],
    )

    with pytest.raises(ValueError) as exc:
        team_service.assign_to_team(NOT_FOUND_ID, STAFF_USER["user_id"], MANAGER_USER["user_id"])
    assert f"Team with id {NOT_FOUND_ID} not found" in str(exc.value)


# INT-062/002
def test_assign_to_team_success(isolated_test_db):

    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], MANAGER_USER["user_id"],
        department_id=VALID_TEAM_CREATE["department_id"],
        team_number=VALID_TEAM_CREATE["team_number"],
    )

    result = team_service.assign_to_team(team["team_id"], STAFF_USER["user_id"], MANAGER_USER["user_id"])

    assert result["team_id"] == team["team_id"]
    assert result["user_id"] == STAFF_USER["user_id"]

    sess = Session(bind=isolated_test_db)
    try:
        assignment = sess.query(TeamAssignment).filter_by(team_id=team["team_id"], user_id=STAFF_USER["user_id"]).one_or_none()
        assert assignment is not None
    finally:
        sess.close()


# INT-062/003
def test_duplicate_assignment_raises_and_only_one_record_exists(isolated_test_db):

    team = team_service.create_team(
        VALID_TEAM_CREATE["team_name"], MANAGER_USER["user_id"],
        department_id=VALID_TEAM_CREATE["department_id"],
        team_number=VALID_TEAM_CREATE["team_number"],
    )

    assignee_id = STAFF_USER["user_id"]
    team_service.assign_to_team(team["team_id"], assignee_id, MANAGER_USER["user_id"])

    with pytest.raises(ValueError):
        team_service.assign_to_team(team["team_id"], assignee_id, MANAGER_USER["user_id"])

    sess = Session(bind=isolated_test_db)
    try:
        assignments = sess.query(TeamAssignment).filter_by(team_id=team["team_id"], user_id=assignee_id).all()
        assert len(assignments) == 1
    finally:
        sess.close()