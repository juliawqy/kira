from __future__ import annotations

import pytest
from sqlalchemy.orm import sessionmaker

import backend.src.handlers.task_handler as task_handler
from backend.src.database.models.user import User
from backend.src.database.models.project import Project
from tests.mock_data.task.integration_data import (
    TASK_CREATE_PAYLOAD,
    VALID_PROJECT,
    VALID_USER_ADMIN,
    VALID_USER_EMPLOYEE,
    TASK_UPDATE_PARTIAL_TITLE,
)


def _serialize_dates(payload: dict) -> dict:
    from datetime import date, datetime
    def convert(v):
        if isinstance(v, (date, datetime)):
            return v.isoformat()
        if isinstance(v, list):
            return [convert(x) for x in v]
        if isinstance(v, dict):
            return {k: convert(vv) for k, vv in v.items()}
        return v
    return {k: convert(v) for k, v in payload.items()}


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


# INT-135/101
@pytest.mark.integration
def test_update_task_shared_recipients_via_api(client, task_base_path, test_engine, clean_db, monkeypatch):
    TestingSessionLocal = sessionmaker(bind=test_engine, future=True)
    with TestingSessionLocal.begin() as db:
        db.add_all([User(**VALID_USER_ADMIN), User(**VALID_USER_EMPLOYEE)])
        db.add(Project(**VALID_PROJECT))

    create_resp = client.post(f"{task_base_path}/", json=_serialize_dates(TASK_CREATE_PAYLOAD))
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    mock_notif = _MockNotifSvc()
    monkeypatch.setattr(task_handler, "get_notification_service", lambda: mock_notif)

    class _Assignee:
        def __init__(self, email):
            self.email = email
    monkeypatch.setattr(
        task_handler.assignment_service,
        "list_assignees",
        lambda tid: [
            _Assignee(VALID_USER_EMPLOYEE["email"]),
            _Assignee(VALID_USER_ADMIN["email"]),
        ],
    )

    patch_payload = {
        "title": TASK_UPDATE_PARTIAL_TITLE["title"],
        "shared_recipient_emails": [VALID_USER_ADMIN["email"]],
    }
    resp = client.patch(f"{task_base_path}/{task_id}", json=patch_payload)
    assert resp.status_code == 200

    call = mock_notif.last_kwargs
    assert call["task_id"] == task_id
    assert call["type_of_alert"] == "task_update"
    recipients = sorted(call.get("to_recipients") or [])
    assert recipients == sorted([VALID_USER_EMPLOYEE["email"], VALID_USER_ADMIN["email"]])
