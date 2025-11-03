import pytest
from sqlalchemy.orm import sessionmaker

import backend.src.handlers.task_handler as task_handler
from backend.src.services import task as task_service
from backend.src.database.models.user import User
from backend.src.database.models.project import Project
from tests.mock_data.task.integration_data import (
    TASK_CREATE_PAYLOAD,
    VALID_PROJECT,
    VALID_USER_ADMIN,
    VALID_USER_EMPLOYEE,
)

class _MockNotifSvc:
    def __init__(self):
        self.last_kwargs = None
        class _Resp:
            success = True
            message = "ok"
            recipients_count = 1
        self._resp = _Resp()
    def notify_activity(self, **kwargs):
        self.last_kwargs = kwargs
        return self._resp

# INT-135/001
def test_update_task_notifies_assignees_and_shared_recipients(test_engine, clean_db, monkeypatch):
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )
    with TestingSessionLocal.begin() as db:
        db.add_all([User(**VALID_USER_ADMIN), User(**VALID_USER_EMPLOYEE)])
        db.add(Project(**VALID_PROJECT))

    monkeypatch.setattr(task_service, "SessionLocal", TestingSessionLocal, raising=False)

    _payload = {k: v for k, v in TASK_CREATE_PAYLOAD.items() if k != "creator_id"}
    task = task_service.add_task(**_payload)

    mock_notif = _MockNotifSvc()
    monkeypatch.setattr(task_handler, "get_notification_service", lambda: mock_notif)
    monkeypatch.setattr(task_handler.user_service, "SessionLocal", TestingSessionLocal, raising=False)
    monkeypatch.setattr(task_handler.task_service, "SessionLocal", TestingSessionLocal, raising=False)
    monkeypatch.setattr(task_handler.assignment_service, "SessionLocal", TestingSessionLocal, raising=False)

    class _Assignee:
        def __init__(self, email):
            self.email = email
    monkeypatch.setattr(
        task_handler.assignment_service,
        "list_assignees",
        lambda task_id: [_Assignee(VALID_USER_EMPLOYEE["email"])],
    )

    updated = task_handler.update_task(
        task.id,
        title="New Title",
        shared_recipient_emails=[VALID_USER_ADMIN["email"]],
        user_email=VALID_USER_ADMIN["email"],
    )

    assert updated.title == "New Title"
    call = mock_notif.last_kwargs
    assert call["task_id"] == task.id
    assert call["type_of_alert"] == "task_update"
    to_recipients = sorted(call.get("to_recipients") or [])
    assert to_recipients == sorted([VALID_USER_EMPLOYEE["email"], VALID_USER_ADMIN["email"]])

# INT-135/002
def test_update_task_shared_recipients_dedup_and_ignore_invalid(test_engine, clean_db, monkeypatch):
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )
    with TestingSessionLocal.begin() as db:
        db.add_all([User(**VALID_USER_ADMIN), User(**VALID_USER_EMPLOYEE)])
        db.add(Project(**VALID_PROJECT))

    # Ensure the task service used for creation writes to the same test DB
    monkeypatch.setattr(task_service, "SessionLocal", TestingSessionLocal, raising=False)

    _payload = {k: v for k, v in TASK_CREATE_PAYLOAD.items() if k != "creator_id"}
    task = task_service.add_task(**_payload)

    mock_notif = _MockNotifSvc()
    monkeypatch.setattr(task_handler, "get_notification_service", lambda: mock_notif)

    # Ensure handler/services use the same test DB
    monkeypatch.setattr(task_handler.user_service, "SessionLocal", TestingSessionLocal, raising=False)
    monkeypatch.setattr(task_handler.task_service, "SessionLocal", TestingSessionLocal, raising=False)
    monkeypatch.setattr(task_handler.assignment_service, "SessionLocal", TestingSessionLocal, raising=False)

    class _Assignee:
        def __init__(self, email):
            self.email = email
    monkeypatch.setattr(
        task_handler.assignment_service,
        "list_assignees",
        lambda task_id: [_Assignee(VALID_USER_EMPLOYEE["email"])],
    )

    task_handler.update_task(
        task.id,
        description="desc",
        shared_recipient_emails=[VALID_USER_ADMIN["email"], VALID_USER_ADMIN["email"], "ghost@example.com"],
        user_email=VALID_USER_EMPLOYEE["email"],
    )

    call = mock_notif.last_kwargs
    to_recipients = sorted(call.get("to_recipients") or [])
    assert to_recipients == sorted([VALID_USER_EMPLOYEE["email"], VALID_USER_ADMIN["email"]])
