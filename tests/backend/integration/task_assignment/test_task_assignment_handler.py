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

# # INT-074/006
# def test_assign_users_task_title_fetch_fails(isolated_test_db, seed_users_and_task):
#     _, handler, m_notif = isolated_test_db
#     with patch("backend.src.handlers.task_assignment_handler.task_service.get_task_with_subtasks", return_value=None):
#         created = handler.assign_users(seed_users_and_task["task_id"], [seed_users_and_task["user_ids"][0]], user_email=ACTOR_EMAIL)
#         assert created == 1
#         call = m_notif.notify_activity.call_args.kwargs
#         assert call["task_title"] == ""

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
def test_assign_users_empty_ids_noop(isolated_test_db, seed_users_and_task):
    _, handler, m_notif = isolated_test_db
    m_notif.notify_activity.reset_mock()
    created = handler.assign_users(task_id=TASK_FOR_ASSIGN_ID, user_ids=[])
    assert created == 0
    m_notif.notify_activity.assert_not_called()

# INT-074/013
def test_unassign_users_empty_ids_noop(isolated_test_db, seed_users_and_task):
    _, handler, m_notif = isolated_test_db
    m_notif.notify_activity.reset_mock()
    deleted = handler.unassign_users(task_id=TASK_FOR_ASSIGN_ID, user_ids=[])
    assert deleted == 0
    m_notif.notify_activity.assert_not_called()

# INT-074/014
def test_assign_users_get_user_missing_email_skips_but_still_notifies_if_any(isolated_test_db, seed_users_and_task):
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
def test_unassign_users_after_list_fails_raises(isolated_test_db, seed_users_and_task):
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

# # INT-074/017
# def test_unassign_users_task_title_fetch_fails(isolated_test_db, seed_users_and_task):
#     _, handler, m_notif = isolated_test_db
#     handler.assign_users(seed_users_and_task["task_id"], seed_users_and_task["user_ids"]) 
#     m_notif.notify_activity.reset_mock()
#     with patch("backend.src.handlers.task_assignment_handler.task_service.get_task_with_subtasks", return_value=None):
#         deleted = handler.unassign_users(seed_users_and_task["task_id"], [seed_users_and_task["user_ids"][0]])
#         assert deleted == 1
#         call = m_notif.notify_activity.call_args.kwargs
#         assert call["task_title"] == ""

# INT-074/018
def test_unassign_users_no_diff_fallback_to_ids(isolated_test_db, seed_users_and_task):
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
def test_unassign_users_before_list_fails_uses_ids_fallback(isolated_test_db, seed_users_and_task):
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
def test_unassign_users_removed_ids_empty_then_fallback_to_ids(isolated_test_db, seed_users_and_task):
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


# # UNI-013/004
# @patch("backend.src.services.task.SessionLocal")
# def test_attach_subtasks_parent_not_found_raises_error(mock_session_local):
#     """Attach subtasks to nonexistent parent raises ValueError"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_session.get.return_value = None
    
#     with pytest.raises(ValueError, match=r"Parent task .* not found"):
#         task_service.attach_subtasks(INVALID_TASK_ID_NONEXISTENT, [VALID_DEFAULT_TASK["id"]])
    
#     mock_session.get.assert_called_once_with(task_service.Task, INVALID_TASK_ID_NONEXISTENT)



# # UNI-013/005
# @patch("backend.src.services.task.SessionLocal")
# def test_attach_subtasks_inactive_parent_raises_error(mock_session_local):
#     """Attach subtasks to inactive parent raises ValueError"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_parent = MagicMock()
#     mock_parent.id = INACTIVE_PARENT_TASK["id"]
#     mock_parent.active = False
#     mock_session.get.return_value = mock_parent
    
#     with pytest.raises(ValueError, match=r"inactive"):
#         task_service.attach_subtasks(INACTIVE_PARENT_TASK["id"], [VALID_DEFAULT_TASK["id"]])



# # UNI-013/005
# @patch("backend.src.services.task.SessionLocal")
# def test_attach_subtasks_inactive_parent_raises_error(mock_session_local):
#     """Attach subtasks to inactive parent raises ValueError"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_parent = MagicMock()
#     mock_parent.id = INACTIVE_PARENT_TASK["id"]
#     mock_parent.active = False
#     mock_session.get.return_value = mock_parent
    
#     with pytest.raises(ValueError, match=r"inactive"):
#         task_service.attach_subtasks(INACTIVE_PARENT_TASK["id"], [VALID_DEFAULT_TASK["id"]])


# # UNI-013/006
# @patch("backend.src.services.task.SessionLocal")
# def test_attach_subtasks_child_not_found_raises_error(mock_session_local):
#     """Attach nonexistent child to parent raises ValueError"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_parent = MagicMock()
#     mock_parent.id = VALID_PARENT_TASK["id"]
#     mock_parent.active = True
#     mock_session.get.return_value = mock_parent
    
#     mock_result = MagicMock()
#     mock_result.scalars.return_value.all.return_value = []
#     mock_session.execute.return_value = mock_result
    
#     with pytest.raises(ValueError, match=r"not found"):
#         task_service.attach_subtasks(VALID_PARENT_TASK["id"], [INVALID_TASK_ID_NONEXISTENT])

# # UNI-013/007
# @patch("backend.src.services.task.SessionLocal")
# def test_attach_subtasks_inactive_child_raises_error(mock_session_local):
#     """Attach inactive child to parent raises ValueError"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_parent = MagicMock()
#     mock_parent.id = VALID_PARENT_TASK["id"]
#     mock_parent.active = True
#     mock_session.get.return_value = mock_parent
    
#     mock_child = MagicMock()
#     mock_child.id = INACTIVE_TASK["id"]
#     mock_child.active = INACTIVE_TASK["active"]
    
#     mock_result = MagicMock()
#     mock_result.scalars.return_value.all.return_value = [mock_child]
#     mock_session.execute.return_value = mock_result
    
#     with pytest.raises(ValueError, match=r"inactive"):
#         task_service.attach_subtasks(VALID_PARENT_TASK["id"], [INACTIVE_TASK["id"]])

# # UNI-013/008
# @patch("backend.src.services.task.SessionLocal")
# def test_attach_subtasks_self_reference_raises_error(mock_session_local):
#     """Attach task to itself as parent raises ValueError"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_parent = MagicMock()
#     mock_parent.id = VALID_PARENT_TASK["id"]
#     mock_parent.active = True
#     mock_session.get.return_value = mock_parent
    
#     with pytest.raises(ValueError, match=r"own parent"):
#         task_service.attach_subtasks(VALID_PARENT_TASK["id"], [VALID_PARENT_TASK["id"]])

# # UNI-023/003
# @patch("backend.src.services.task.SessionLocal")
# def test_detach_subtask_nonexistent_link_raises_error(mock_session_local):
#     """Detach nonexistent parent-child link raises ValueError"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_session.execute.return_value.scalar_one_or_none.return_value = None
    
#     with pytest.raises(ValueError, match=r"Link not found|not found"):
#         task_service.detach_subtask(VALID_PARENT_TASK["id"], VALID_DEFAULT_TASK["id"])

# # UNI-023/004
# @patch("backend.src.services.task.SessionLocal")
# def test_detach_subtask_nonexistent_parent_raises_error(mock_session_local):
#     """Detach from nonexistent parent raises ValueError"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_session.execute.return_value.scalar_one_or_none.return_value = None
    
#     with pytest.raises(ValueError, match=r"Link not found|not found"):
#         task_service.detach_subtask(INVALID_TASK_ID_NONEXISTENT, VALID_DEFAULT_TASK["id"])

# # UNI-023/005
# @patch("backend.src.services.task.SessionLocal")
# def test_detach_subtask_nonexistent_child_raises_error(mock_session_local):
#     """Detach nonexistent child from parent raises ValueError"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_session.execute.return_value.scalar_one_or_none.return_value = None
    
#     with pytest.raises(ValueError, match=r"Link not found|not found"):
#         task_service.detach_subtask(VALID_PARENT_TASK["id"], INVALID_TASK_ID_NONEXISTENT)



# # UNI-023/006
# @patch("backend.src.services.task.SessionLocal")
# def test_detach_subtask_idempotent_behavior(mock_session_local):
#     """Re-detaching same child is idempotent (raises error consistently)"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_session.execute.return_value.scalar_one_or_none.return_value = None
    
#     with pytest.raises(ValueError, match=r"Link not found|not found"):
#         task_service.detach_subtask(VALID_PARENT_TASK["id"], VALID_DEFAULT_TASK["id"])

# # UNI-023/007
# @patch("backend.src.services.task.SessionLocal")
# def test_detach_subtask_from_inactive_parent_raises_error(mock_session_local):
#     """Detach subtask from inactive parent raises ValueError"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_session.execute.return_value.scalar_one_or_none.return_value = None
    
#     with pytest.raises(ValueError, match=r"Link not found|not found"):
#         task_service.detach_subtask(INACTIVE_PARENT_TASK["id"], VALID_DEFAULT_TASK["id"])

# # UNI-023/008
# @patch("backend.src.services.task.SessionLocal")
# def test_detach_inactive_subtask_raises_error(mock_session_local):
#     """Detach inactive subtask from parent raises ValueError"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_session.execute.return_value.scalar_one_or_none.return_value = None
    
#     with pytest.raises(ValueError, match=r"Link not found|not found"):
#         task_service.detach_subtask(VALID_PARENT_TASK["id"], INACTIVE_TASK["id"])

# # UNI-023/010
# @patch("backend.src.services.task.SessionLocal")
# def test_detach_subtask_multiple_operations_maintain_consistency(mock_session_local):
#     """Multiple detach operations maintain data consistency"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_link1 = MagicMock()
#     mock_link1.parent_id = VALID_PARENT_TASK["id"]
#     mock_link1.subtask_id = VALID_DEFAULT_TASK["id"]
    
#     mock_link2 = MagicMock()
#     mock_link2.parent_id = VALID_PARENT_TASK["id"]
#     mock_link2.subtask_id = VALID_TASK_EXPLICIT_PRIORITY["id"]
    
#     call_count = 0
#     def mock_execute_side_effect(*args, **kwargs):
#         nonlocal call_count
#         call_count += 1
#         if call_count == 1:
#             mock_result = MagicMock()
#             mock_result.scalar_one_or_none.return_value = mock_link1
#             return mock_result
#         elif call_count == 2:
#             mock_result = MagicMock()
#             mock_result.scalar_one_or_none.return_value = mock_link2
#             return mock_result
#         else:
#             mock_result = MagicMock()
#             mock_result.scalar_one_or_none.return_value = None
#             return mock_result
    
#     mock_session.execute.side_effect = mock_execute_side_effect
    
#     result1 = task_service.detach_subtask(VALID_PARENT_TASK["id"], VALID_DEFAULT_TASK["id"])
#     result2 = task_service.detach_subtask(VALID_PARENT_TASK["id"], VALID_TASK_EXPLICIT_PRIORITY["id"])
    
#     assert result1 is True
#     assert result2 is True
#     assert mock_session.delete.call_count == 2
    
#     with pytest.raises(ValueError, match=r"Link not found|not found"):
#         task_service.detach_subtask(VALID_PARENT_TASK["id"], VALID_DEFAULT_TASK["id"])



# # UNI-013/011
# @patch("backend.src.services.task.SessionLocal")
# def test_attach_subtasks_partial_failure_all_or_nothing(mock_session_local):
#     """If one child ID is invalid, no children are attached (all-or-nothing)"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_parent = MagicMock()
#     mock_parent.id = VALID_PARENT_TASK["id"]
#     mock_parent.active = True
#     mock_session.get.return_value = mock_parent
    
#     mock_child = MagicMock()
#     mock_child.id = VALID_DEFAULT_TASK["id"]
#     mock_child.active = True
    
#     mock_result = MagicMock()
#     mock_result.scalars.return_value.all.return_value = [mock_child]
#     mock_session.execute.return_value = mock_result
    
#     with pytest.raises(ValueError, match=r"not found"):
#         task_service.attach_subtasks(VALID_PARENT_TASK["id"], [VALID_DEFAULT_TASK["id"], INVALID_TASK_ID_NONEXISTENT])
    
#     mock_session.add.assert_not_called()
    
#     mock_session.execute.return_value.scalar_one_or_none.return_value = mock_parent
    
#     parent_with_subtasks = task_service.get_task_with_subtasks(VALID_PARENT_TASK["id"])
#     assert parent_with_subtasks is not None
#     assert len(parent_with_subtasks.subtasks) == 0

# # UNI-013/012
# @patch("backend.src.services.task.SessionLocal")
# def test_attach_subtasks_empty_list_returns_parent(mock_session_local):
#     """Attach empty list of children returns parent unchanged"""
#     from backend.src.services import task as task_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_parent = MagicMock()
#     mock_parent.id = VALID_PARENT_TASK["id"]
#     mock_parent.active = True
#     mock_parent.subtasks = []
#     mock_session.get.return_value = mock_parent
    
#     mock_session.execute.return_value.scalar_one.return_value = mock_parent
    
#     result = task_service.attach_subtasks(VALID_PARENT_TASK["id"], [])
    
#     mock_session.get.assert_called_once_with(task_service.Task, VALID_PARENT_TASK["id"])
#     assert result == mock_parent
    
#     mock_session.execute.return_value.scalar_one_or_none.return_value = mock_parent
    
#     parent_with_subtasks = task_service.get_task_with_subtasks(VALID_PARENT_TASK["id"])
#     assert parent_with_subtasks is not None
#     assert len(parent_with_subtasks.subtasks) == 0


# # UNI-026/006
# @patch("backend.src.services.task_assignment.SessionLocal")
# def test_assign_users_deduplicates_user_ids(mock_session_local):
#     """Assign users with duplicate IDs deduplicates and processes correctly"""
#     from backend.src.services import task_assignment as ta_service
    
#     mock_session = MagicMock()
#     mock_session_local.begin.return_value.__enter__.return_value = mock_session
    
#     mock_task = MagicMock()
#     mock_task.id = VALID_DEFAULT_TASK["id"]
#     mock_task.active = True
#     mock_session.get.return_value = mock_task
    
#     mock_user = MagicMock()
#     mock_user.user_id = VALID_USER_ADMIN["user_id"]
    
#     def mock_execute_side_effect(stmt):
#         if "user_id" in str(stmt).lower() and "where" in str(stmt).lower():
#             if "in" in str(stmt).lower():
#                 mock_result = MagicMock()
#                 mock_result.scalars.return_value.all.return_value = [mock_user]
#                 return mock_result
#             else:
#                 mock_result = MagicMock()
#                 mock_result.scalars.return_value.all.return_value = []
#                 return mock_result
    
#     mock_session.execute.side_effect = mock_execute_side_effect
    
#     user_ids = [VALID_USER_ADMIN["user_id"], VALID_USER_ADMIN["user_id"], VALID_USER_ADMIN["user_id"]]
#     result = ta_service.assign_users(VALID_DEFAULT_TASK["id"], user_ids)
    
#     assert result == 1  
#     assert mock_session.add.call_count == 1