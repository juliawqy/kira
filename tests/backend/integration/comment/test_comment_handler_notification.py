import pytest
from sqlalchemy.orm import sessionmaker

from backend.src.database.models.user import User
from backend.src.database.models.task import Task
from backend.src.database.models.project import Project

from backend.src.enums.notification import NotificationType
import backend.src.handlers.comment_handler as comment_handler

from tests.mock_data.comment.integration_data import (
    VALID_USER,
    ANOTHER_USER,
    VALID_PROJECT,
    VALID_TASK,
    INVALID_TASK_ID,
    INVALID_USER_ID,
    COMMENT_CREATE_NONEXISTENT_RECIPIENTS_PAYLOAD,
)

class _MockNotifSvc:
    def __init__(self):
        self.last_kwargs = None
        class _Resp:
            success = True
            message = "ok"
            recipients_count = 2
        self._resp = _Resp()

    def notify_activity(self, **kwargs):
        self.last_kwargs = kwargs
        return self._resp

class _MockAssignee:
    def __init__(self, email: str):
        self.email = email

@pytest.fixture(autouse=True)
def use_test_db(test_engine, monkeypatch):
    from backend.src.services import task, comment, user

    TestSessionLocal = sessionmaker(bind=test_engine, future=True)
    monkeypatch.setattr(task, "SessionLocal", TestSessionLocal)
    monkeypatch.setattr(comment, "SessionLocal", TestSessionLocal)
    monkeypatch.setattr(user, "SessionLocal", TestSessionLocal)

@pytest.fixture
def seed_task_and_users(test_engine):
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        user1 = User(**VALID_USER)
        user2 = User(**ANOTHER_USER)
        db.add_all([user1, user2])
        db.flush()
        project = Project(**VALID_PROJECT)
        task = Task(**VALID_TASK)
        db.add_all([project, task])
    yield

# INT-034/001
def test_add_comment_triggers_notification_with_recipients_and_assignees(
    seed_task_and_users, monkeypatch
):
    mock_notif = _MockNotifSvc()
    monkeypatch.setattr(comment_handler, "get_notification_service", lambda: mock_notif)
    monkeypatch.setattr(
        comment_handler.assignment_service,
        "list_assignees",
        lambda task_id: [_MockAssignee(ANOTHER_USER["email"])],
    )

    result = comment_handler.add_comment(
        task_id=VALID_TASK["id"],
        user_id=VALID_USER["user_id"],
        comment_text="hi",
        recipient_emails=[
            VALID_USER["email"],
            ANOTHER_USER["email"],
            COMMENT_CREATE_NONEXISTENT_RECIPIENTS_PAYLOAD["recipient_emails"][0],
        ],
    )

    assert result["task_id"] == VALID_TASK["id"]
    assert mock_notif.last_kwargs is not None

    call = mock_notif.last_kwargs
    assert call["type_of_alert"] == NotificationType.COMMENT_CREATE.value
    assert call["task_id"] == VALID_TASK["id"]
    assert call["task_title"] == VALID_TASK["title"]
    assert call["user_email"] == VALID_USER["email"]
    assert call["comment_user"] == VALID_USER["name"]

    to_recipients = sorted(call.get("to_recipients") or [])
    assert to_recipients == sorted([VALID_USER["email"], ANOTHER_USER["email"]])

# INT-034/002
def test_add_comment_notification_no_payload_and_no_assignees(
    seed_task_and_users, monkeypatch
):
    mock_notif = _MockNotifSvc()
    monkeypatch.setattr(comment_handler, "get_notification_service", lambda: mock_notif)
    monkeypatch.setattr(
        comment_handler.assignment_service,
        "list_assignees",
        lambda task_id: [],
    )

    result = comment_handler.add_comment(
        task_id=VALID_TASK["id"],
        user_id=VALID_USER["user_id"],
        comment_text="hi",
    )

    assert result["task_id"] == VALID_TASK["id"]
    call = mock_notif.last_kwargs
    assert call["type_of_alert"] == NotificationType.COMMENT_CREATE.value
    assert call.get("to_recipients") is None


# INT-034/003
def test_add_comment_ignores_assignee_without_email(
    seed_task_and_users, monkeypatch
):
    mock_notif = _MockNotifSvc()
    monkeypatch.setattr(comment_handler, "get_notification_service", lambda: mock_notif)
    monkeypatch.setattr(
        comment_handler.assignment_service,
        "list_assignees",
        lambda task_id: [_MockAssignee(None)],
    )

    result = comment_handler.add_comment(
        task_id=VALID_TASK["id"],
        user_id=VALID_USER["user_id"],
        comment_text="hi",
        recipient_emails=[VALID_USER["email"]],
    )

    assert result["task_id"] == VALID_TASK["id"]
    call = mock_notif.last_kwargs
    assert call["type_of_alert"] == NotificationType.COMMENT_CREATE.value
    assert sorted(call.get("to_recipients") or []) == [VALID_USER["email"]]


# INT-034/004
def test_add_comment_two_valid_payload_no_assignees(
    seed_task_and_users, monkeypatch
):
    mock_notif = _MockNotifSvc()
    monkeypatch.setattr(comment_handler, "get_notification_service", lambda: mock_notif)
    monkeypatch.setattr(
        comment_handler.assignment_service,
        "list_assignees",
        lambda task_id: [],
    )

    result = comment_handler.add_comment(
        task_id=VALID_TASK["id"],
        user_id=VALID_USER["user_id"],
        comment_text="hi",
        recipient_emails=[VALID_USER["email"], ANOTHER_USER["email"], VALID_USER["email"]],
    )

    assert result["task_id"] == VALID_TASK["id"]
    call = mock_notif.last_kwargs
    assert call["type_of_alert"] == NotificationType.COMMENT_CREATE.value
    assert sorted(call.get("to_recipients") or []) == sorted([VALID_USER["email"], ANOTHER_USER["email"]])


# INT-034/005
def test_notify_comment_mentions_sends_to_valid_recipients(seed_task_and_users, monkeypatch):
    mock_notif = _MockNotifSvc()
    monkeypatch.setattr(comment_handler, "get_notification_service", lambda: mock_notif)

    resp = comment_handler.notify_comment_mentions(
        task_id=VALID_TASK["id"],
        user_id=VALID_USER["user_id"],
        recipient_emails=[VALID_USER["email"], ANOTHER_USER["email"]],
    )

    assert getattr(resp, "success", False) is True
    call = mock_notif.last_kwargs
    assert call["type_of_alert"] == NotificationType.COMMENT_MENTION.value
    assert call["task_id"] == VALID_TASK["id"]
    assert call["task_title"] == VALID_TASK["title"]
    assert call["user_email"] == VALID_USER["email"]
    assert call["comment_user"] == VALID_USER["name"]
    assert sorted(call.get("to_recipients") or []) == sorted([VALID_USER["email"], ANOTHER_USER["email"]])


# INT-034/006
def test_notify_comment_mentions_loop_backedge_with_three_recipients(
    seed_task_and_users, monkeypatch
):
    mock_notif = _MockNotifSvc()
    monkeypatch.setattr(comment_handler, "get_notification_service", lambda: mock_notif)

    resp = comment_handler.notify_comment_mentions(
        task_id=VALID_TASK["id"],
        user_id=VALID_USER["user_id"],
        recipient_emails=[VALID_USER["email"], ANOTHER_USER["email"], VALID_USER["email"]],
    )

    assert getattr(resp, "success", False) is True
    call = mock_notif.last_kwargs
    assert call["type_of_alert"] == NotificationType.COMMENT_MENTION.value
    assert sorted(call.get("to_recipients") or []) == sorted([VALID_USER["email"], ANOTHER_USER["email"]])


# INT-034/007
def test_notify_comment_mentions_returns_none_when_empty_list(seed_task_and_users, monkeypatch):
    mock_notif = _MockNotifSvc()
    monkeypatch.setattr(comment_handler, "get_notification_service", lambda: mock_notif)
    resp = comment_handler.notify_comment_mentions(
        task_id=VALID_TASK["id"], user_id=VALID_USER["user_id"], recipient_emails=[]
    )
    assert resp is None
    assert mock_notif.last_kwargs is None


# INT-034/008
def test_notify_comment_mentions_returns_none_when_all_nonexistent(seed_task_and_users, monkeypatch):
    mock_notif = _MockNotifSvc()
    monkeypatch.setattr(comment_handler, "get_notification_service", lambda: mock_notif)
    resp = comment_handler.notify_comment_mentions(
        task_id=VALID_TASK["id"],
        user_id=VALID_USER["user_id"],
        recipient_emails=COMMENT_CREATE_NONEXISTENT_RECIPIENTS_PAYLOAD["recipient_emails"],
    )
    assert resp is None
    assert mock_notif.last_kwargs is None


# INT-034/009
def test_notify_comment_mentions_raises_when_task_missing(seed_task_and_users, monkeypatch):
    mock_notif = _MockNotifSvc()
    monkeypatch.setattr(comment_handler, "get_notification_service", lambda: mock_notif)
    with pytest.raises(ValueError):
        comment_handler.notify_comment_mentions(
            task_id=INVALID_TASK_ID,
            user_id=VALID_USER["user_id"],
            recipient_emails=[VALID_USER["email"]],
        )


# INT-034/010
def test_notify_comment_mentions_raises_when_user_missing(seed_task_and_users, monkeypatch):
    mock_notif = _MockNotifSvc()
    monkeypatch.setattr(comment_handler, "get_notification_service", lambda: mock_notif)
    with pytest.raises(ValueError):
        comment_handler.notify_comment_mentions(
            task_id=VALID_TASK["id"],
            user_id=INVALID_USER_ID,
            recipient_emails=[VALID_USER["email"]],
        )


# INT-034/011
def test_notify_comment_mentions_deduplicates_recipients(seed_task_and_users, monkeypatch):
    mock_notif = _MockNotifSvc()
    monkeypatch.setattr(comment_handler, "get_notification_service", lambda: mock_notif)
    resp = comment_handler.notify_comment_mentions(
        task_id=VALID_TASK["id"],
        user_id=VALID_USER["user_id"],
        recipient_emails=[VALID_USER["email"], VALID_USER["email"]],
    )
    assert getattr(resp, "success", False) is True
    call = mock_notif.last_kwargs
    assert call["type_of_alert"] == NotificationType.COMMENT_MENTION.value
    assert sorted(call.get("to_recipients") or []) == [VALID_USER["email"]]