from __future__ import annotations

import os
import tempfile
import importlib
import pytest
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from backend.src.database.db_setup import Base
from backend.src.database.models.user import User
from backend.src.database.models.task import Task
from backend.src.database.models.task_assignment import TaskAssignment
from backend.src.enums.notification import NotificationType
from backend.src.schemas.email import EmailResponse

from tests.mock_data.task_assignment.task_assign_data import (
    USER_ADMIN,
    USER_EMPLOYEE,
    USER_ADMIN_ID,
    USER_EMPLOYEE_ID,
    USER_IDS_FOR_ASSIGN,
)
from tests.mock_data.task_assignment.task_assignment_data import TASK_FOR_ASSIGN, TASK_FOR_ASSIGN_ID, ACTOR_EMAIL


@pytest.fixture(autouse=True)
def clean_db(test_engine):
    TestingSession = sessionmaker(bind=test_engine, future=True)
    with TestingSession.begin() as s:
        s.execute(delete(TaskAssignment))
        s.execute(delete(Task))
        s.execute(delete(User))
    yield


@pytest.fixture
def isolated_test_db():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    test_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine)

    with patch("backend.src.services.task.SessionLocal", TestSessionLocal), \
         patch("backend.src.services.user.SessionLocal", TestSessionLocal), \
         patch("backend.src.services.task_assignment.SessionLocal", TestSessionLocal), \
         patch("backend.src.handlers.task_assignment_handler.task_service.SessionLocal", TestSessionLocal), \
         patch("backend.src.handlers.task_assignment_handler.user_service.SessionLocal", TestSessionLocal), \
         patch("backend.src.handlers.task_assignment_handler.assignment_service.SessionLocal", TestSessionLocal), \
         patch("backend.src.handlers.task_assignment_handler.get_notification_service") as mock_get_notif:

        m_notif = MagicMock()
        m_notif.notify_activity.return_value = EmailResponse(success=True, message="ok", recipients_count=1)
        mock_get_notif.return_value = m_notif

        task_assignment_handler = importlib.import_module("backend.src.handlers.task_assignment_handler")
        yield test_engine, task_assignment_handler, m_notif

    try:
        test_engine.dispose()
        os.unlink(db_path)
    except (OSError, PermissionError):
        pass


@pytest.fixture
def seed_users_and_task(isolated_test_db):
    test_engine, _, _ = isolated_test_db
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        u1 = User(user_id=USER_ADMIN_ID, **USER_ADMIN)
        u2 = User(user_id=USER_EMPLOYEE_ID, **USER_EMPLOYEE)
        db.add_all([u1, u2])
        t = Task(**TASK_FOR_ASSIGN)
        db.add(t)
    return {"task_id": TASK_FOR_ASSIGN_ID, "user_ids": USER_IDS_FOR_ASSIGN}

# INT-074/001
def test_assign_users_notifies(isolated_test_db, seed_users_and_task):
    _, handler, m_notif = isolated_test_db
    created = handler.assign_users(seed_users_and_task["task_id"], seed_users_and_task["user_ids"], user_email=ACTOR_EMAIL)
    assert created == 2
    m_notif.notify_activity.assert_called_once()
    call = m_notif.notify_activity.call_args.kwargs
    assert call["user_email"] == ACTOR_EMAIL
    assert call["task_id"] == seed_users_and_task["task_id"]
    assert call["task_title"] == TASK_FOR_ASSIGN["title"]
    assert call["type_of_alert"] == NotificationType.TASK_ASSIGN.value
    assert sorted(call["to_recipients"]) == [USER_ADMIN["email"], USER_EMPLOYEE["email"]]

# INT-074/002
def test_unassign_users_notifies_removed(isolated_test_db, seed_users_and_task):
    _, handler, m_notif = isolated_test_db
    handler.assign_users(seed_users_and_task["task_id"], seed_users_and_task["user_ids"], user_email=ACTOR_EMAIL)
    m_notif.notify_activity.reset_mock()

    deleted = handler.unassign_users(seed_users_and_task["task_id"], [seed_users_and_task["user_ids"][0]] , user_email=ACTOR_EMAIL)
    assert deleted == 1
    m_notif.notify_activity.assert_called_once()
    call = m_notif.notify_activity.call_args.kwargs
    assert call["type_of_alert"] == NotificationType.TASK_UNASSIGN.value
    assert call["to_recipients"] == [USER_ADMIN["email"]]

# INT-074/003
def test_assign_users_idempotent(isolated_test_db, seed_users_and_task):
    _, handler, m_notif = isolated_test_db
    first = handler.assign_users(seed_users_and_task["task_id"], seed_users_and_task["user_ids"]) 
    assert first == 2
    m_notif.notify_activity.reset_mock()
    second = handler.assign_users(seed_users_and_task["task_id"], [seed_users_and_task["user_ids"][0]])
    assert second == 0
    m_notif.notify_activity.assert_not_called()

# INT-074/004
def test_unassign_users_no_assignments(isolated_test_db, seed_users_and_task):
    _, handler, m_notif = isolated_test_db
    deleted = handler.unassign_users(seed_users_and_task["task_id"], seed_users_and_task["user_ids"]) 
    assert deleted == 0
    m_notif.notify_activity.assert_not_called()

# INT-074/005
def test_assign_users_before_list_fails(isolated_test_db, seed_users_and_task):
    test_engine, handler, m_notif = isolated_test_db
    with patch("backend.src.handlers.task_assignment_handler.assignment_service.list_assignees") as m_list:
        # before fails, after succeeds
        m_list.side_effect = [Exception("boom"), [MagicMock(user_id=seed_users_and_task["user_ids"][0]), MagicMock(user_id=seed_users_and_task["user_ids"][1])]]
        created = handler.assign_users(seed_users_and_task["task_id"], seed_users_and_task["user_ids"], user_email=ACTOR_EMAIL)
        assert created == 2
        m_notif.notify_activity.assert_called_once()

# INT-074/006
def test_assign_users_task_title_fetch_fails(isolated_test_db, seed_users_and_task):
    _, handler, m_notif = isolated_test_db
    with patch("backend.src.handlers.task_assignment_handler.task_service.get_task_with_subtasks", return_value=None):
        created = handler.assign_users(seed_users_and_task["task_id"], [seed_users_and_task["user_ids"][0]], user_email=ACTOR_EMAIL)
        assert created == 1
        call = m_notif.notify_activity.call_args.kwargs
        assert call["task_title"] == ""

# INT-074/007
def test_assign_users_notify_exception_raises(isolated_test_db, seed_users_and_task):
    _, handler, _ = isolated_test_db
    with patch("backend.src.handlers.task_assignment_handler.get_notification_service") as mock_get_notif:
        m_notif = MagicMock()
        m_notif.notify_activity.side_effect = Exception("boom")
        mock_get_notif.return_value = m_notif
        with pytest.raises(Exception):
            handler.assign_users(seed_users_and_task["task_id"], seed_users_and_task["user_ids"], user_email=ACTOR_EMAIL)

# INT-074/008
def test_unassign_users_notify_exception_raises(isolated_test_db, seed_users_and_task):
    _, handler, _ = isolated_test_db
    handler.assign_users(seed_users_and_task["task_id"], seed_users_and_task["user_ids"])  
    with patch("backend.src.handlers.task_assignment_handler.get_notification_service") as mock_get_notif:
        m_notif = MagicMock()
        m_notif.notify_activity.side_effect = Exception("nope")
        mock_get_notif.return_value = m_notif
        with pytest.raises(Exception):
            handler.unassign_users(seed_users_and_task["task_id"], [seed_users_and_task["user_ids"][0]])

# INT-074/009
def test_assign_users_logger_info_failure_raises(isolated_test_db, seed_users_and_task):
    _, handler, m_notif = isolated_test_db
    with patch("backend.src.handlers.task_assignment_handler.logger.info", side_effect=Exception("logfail")):
        with pytest.raises(Exception):
            handler.assign_users(seed_users_and_task["task_id"], seed_users_and_task["user_ids"]) 

# INT-074/010
def test_unassign_users_logger_info_failure_raises(isolated_test_db, seed_users_and_task):
    _, handler, m_notif = isolated_test_db
    handler.assign_users(seed_users_and_task["task_id"], seed_users_and_task["user_ids"]) 
    with patch("backend.src.handlers.task_assignment_handler.logger.info", side_effect=Exception("logfail")):
        with pytest.raises(Exception):
            handler.unassign_users(seed_users_and_task["task_id"], [seed_users_and_task["user_ids"][0]])

# INT-074/011
def test_assign_users_no_emails_no_notify_integration(isolated_test_db, seed_users_and_task):
    _, handler, m_notif = isolated_test_db
    m_notif.notify_activity.reset_mock()
    with patch("backend.src.handlers.task_assignment_handler.user_service.get_user", side_effect=lambda uid: MagicMock(email=None)):
        created = handler.assign_users(seed_users_and_task["task_id"], seed_users_and_task["user_ids"]) 
        assert created == 2
        m_notif.notify_activity.assert_not_called()

# INT-074/012
def test_assign_users_empty_ids_noop(isolated_test_db):
    _, handler, m_notif = isolated_test_db
    m_notif.notify_activity.reset_mock()
    created = handler.assign_users(task_id=TASK_FOR_ASSIGN_ID, user_ids=[])
    assert created == 0
    m_notif.notify_activity.assert_not_called()

# INT-074/013
def test_unassign_users_empty_ids_noop(isolated_test_db):
    _, handler, m_notif = isolated_test_db
    m_notif.notify_activity.reset_mock()
    deleted = handler.unassign_users(task_id=TASK_FOR_ASSIGN_ID, user_ids=[])
    assert deleted == 0
    m_notif.notify_activity.assert_not_called()


# INT-074/014
def test_assign_users_get_user_missing_email_skips_but_still_notifies_if_any(isolated_test_db):
    _, handler, m_notif = isolated_test_db
    m_notif.notify_activity.reset_mock()
    with patch("backend.src.handlers.task_assignment_handler.assignment_service.list_assignees") as m_list, \
         patch("backend.src.handlers.task_assignment_handler.assignment_service.assign_users", return_value=2), \
         patch("backend.src.handlers.task_assignment_handler.user_service.get_user") as m_get_user:
        m_list.side_effect = [[], [MagicMock(user_id=USER_ADMIN_ID), MagicMock(user_id=USER_EMPLOYEE_ID)]]
        def _fake_get(uid):
            if uid == USER_ADMIN_ID:
                return MagicMock(email=None)
            return MagicMock(email=USER_EMPLOYEE["email"]) 
        m_get_user.side_effect = _fake_get
        created = handler.assign_users(task_id=TASK_FOR_ASSIGN_ID, user_ids=USER_IDS_FOR_ASSIGN)
        assert created == 2
    m_notif.notify_activity.assert_called_once()
    emails = m_notif.notify_activity.call_args.kwargs["to_recipients"]
    assert emails == [USER_EMPLOYEE["email"]]


# INT-074/015
def test_unassign_users_after_list_fails_raises(isolated_test_db):
    _, handler, m_notif = isolated_test_db
    m_notif.notify_activity.reset_mock()
    with patch("backend.src.handlers.task_assignment_handler.assignment_service.list_assignees") as m_list, \
         patch("backend.src.handlers.task_assignment_handler.assignment_service.unassign_users", return_value=2), \
         patch("backend.src.handlers.task_assignment_handler.user_service.get_user", return_value=MagicMock(email=USER_EMPLOYEE["email"])):
        m_list.side_effect = [[MagicMock(user_id=USER_ADMIN_ID), MagicMock(user_id=USER_EMPLOYEE_ID)], Exception("after fail")]
        with pytest.raises(Exception):
            handler.unassign_users(task_id=TASK_FOR_ASSIGN_ID, user_ids=USER_IDS_FOR_ASSIGN)


# INT-074/016
def test_unassign_users_no_emails_no_notify_integration(isolated_test_db, seed_users_and_task):
    _, handler, m_notif = isolated_test_db
    handler.assign_users(seed_users_and_task["task_id"], seed_users_and_task["user_ids"]) 
    m_notif.notify_activity.reset_mock()
    with patch("backend.src.handlers.task_assignment_handler.user_service.get_user", side_effect=lambda uid: MagicMock(email=None)):
        deleted = handler.unassign_users(seed_users_and_task["task_id"], seed_users_and_task["user_ids"]) 
        assert deleted == 2
        m_notif.notify_activity.assert_not_called()


# INT-074/017
def test_unassign_users_task_title_fetch_fails(isolated_test_db, seed_users_and_task):
    _, handler, m_notif = isolated_test_db
    handler.assign_users(seed_users_and_task["task_id"], seed_users_and_task["user_ids"]) 
    m_notif.notify_activity.reset_mock()
    with patch("backend.src.handlers.task_assignment_handler.task_service.get_task_with_subtasks", return_value=None):
        deleted = handler.unassign_users(seed_users_and_task["task_id"], [seed_users_and_task["user_ids"][0]])
        assert deleted == 1
        call = m_notif.notify_activity.call_args.kwargs
        assert call["task_title"] == ""


# INT-074/018
def test_unassign_users_no_diff_fallback_to_ids(isolated_test_db):
    _, handler, m_notif = isolated_test_db
    m_notif.notify_activity.reset_mock()
    ids = USER_IDS_FOR_ASSIGN
    before_list = [MagicMock(user_id=USER_ADMIN_ID), MagicMock(user_id=USER_EMPLOYEE_ID)]
    after_list = [MagicMock(user_id=USER_ADMIN_ID), MagicMock(user_id=USER_EMPLOYEE_ID)]
    with patch("backend.src.handlers.task_assignment_handler.assignment_service.list_assignees") as m_list, \
         patch("backend.src.handlers.task_assignment_handler.assignment_service.unassign_users", return_value=2), \
         patch("backend.src.handlers.task_assignment_handler.user_service.get_user", return_value=MagicMock(email="x@example.com")):
        m_list.side_effect = [before_list, after_list]
        deleted = handler.unassign_users(task_id=TASK_FOR_ASSIGN_ID, user_ids=ids)
        assert deleted == 2
        m_notif.notify_activity.assert_called_once()
        emails = m_notif.notify_activity.call_args.kwargs["to_recipients"]
        assert sorted(emails) == ["x@example.com", "x@example.com"]


# INT-074/019
def test_unassign_users_before_list_fails_uses_ids_fallback(isolated_test_db):
    _, handler, m_notif = isolated_test_db
    m_notif.notify_activity.reset_mock()
    with patch("backend.src.handlers.task_assignment_handler.assignment_service.list_assignees") as m_list, \
         patch("backend.src.handlers.task_assignment_handler.assignment_service.unassign_users", return_value=2), \
         patch("backend.src.handlers.task_assignment_handler.user_service.get_user", return_value=MagicMock(email="y@example.com")):
        m_list.side_effect = [Exception("before fail"), []]
        deleted = handler.unassign_users(task_id=TASK_FOR_ASSIGN_ID, user_ids=USER_IDS_FOR_ASSIGN)
        assert deleted == 2
        m_notif.notify_activity.assert_called_once()
        emails = m_notif.notify_activity.call_args.kwargs["to_recipients"]
        assert sorted(emails) == ["y@example.com", "y@example.com"]


# INT-074/020
def test_unassign_users_removed_ids_empty_then_fallback_to_ids(isolated_test_db):
    _, handler, m_notif = isolated_test_db
    m_notif.notify_activity.reset_mock()
    with patch("backend.src.handlers.task_assignment_handler.assignment_service.list_assignees") as m_list, \
         patch("backend.src.handlers.task_assignment_handler.assignment_service.unassign_users", return_value=1), \
         patch("backend.src.handlers.task_assignment_handler.user_service.get_user", return_value=MagicMock(email="z@example.com")):
        m_list.side_effect = [[MagicMock(user_id=USER_ADMIN_ID)], [MagicMock(user_id=USER_ADMIN_ID)]]
        deleted = handler.unassign_users(task_id=TASK_FOR_ASSIGN_ID, user_ids=[USER_ADMIN_ID])
        assert deleted == 1
        m_notif.notify_activity.assert_called_once()
        emails = m_notif.notify_activity.call_args.kwargs["to_recipients"]
        assert emails == ["z@example.com"]
