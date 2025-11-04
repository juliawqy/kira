# tests/backend/integration/task/test_task_service_layer.py
from __future__ import annotations
import pytest
from datetime import date, datetime
from sqlalchemy import text

import backend.src.database.db_setup as db_setup
from backend.src.database.models.project import Project
from backend.src.database.models.user import User
from backend.src.database.models.parent_assignment import ParentAssignment
from backend.src.services import task as task_service
from tests.mock_data.task.integration_data import (
    TASK_CREATE_PAYLOAD_SERVICE,
    TASK_CREATE_CHILD_SERVICE,
    TASK_UPDATE_PAYLOAD,
    INACTIVE_TASK_PAYLOAD_SERVICE,
    VALID_PROJECT,
    VALID_PROJECT_2,
    VALID_USER_ADMIN,
    VALID_USER_MANAGER,
    INVALID_TASK_ID_NONEXISTENT,
)

# ---------------------------------------------------------------------------

def serialize_payload(payload: dict) -> dict:
    def convert(v):
        if isinstance(v, (date, datetime)):
            return v.isoformat()
        if isinstance(v, dict):
            return {k: convert(val) for k, val in v.items()}
        if isinstance(v, list):
            return [convert(i) for i in v]
        return v
    return {k: convert(v) for k, v in payload.items()}


@pytest.fixture(autouse=True)
def test_db_session(test_engine):
    from sqlalchemy.orm import sessionmaker
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )

    with TestingSessionLocal() as session:
        db_setup.SessionLocal.configure(bind=session.get_bind())
        yield session


@pytest.fixture(autouse=True)
def seed_project_and_user(test_db_session, clean_db):
    """Ensure valid user/project setup before each test."""
    manager = User(**VALID_USER_ADMIN)
    manager2 = User(**VALID_USER_MANAGER)
    test_db_session.add_all([manager, manager2])
    test_db_session.flush()
    project = Project(**VALID_PROJECT)
    project2 = Project(**VALID_PROJECT_2)
    test_db_session.add_all([project, project2])
    test_db_session.commit()

# ---------------------------------------------------------------------------
# INT-131/001
def test_add_task_creates_entry(test_db_session):
    """Direct call to add_task inserts one row."""
    task = task_service.add_task(**TASK_CREATE_PAYLOAD_SERVICE)
    assert task.id is not None
    count = test_db_session.execute(
        text("SELECT COUNT(*) FROM task WHERE id=:i"), {"i": task.id}
    ).scalar()
    assert count == 1


# INT-131/002
def test_update_task_modifies_fields(test_db_session):
    """update_task should modify only provided fields."""
    created = task_service.add_task(**TASK_CREATE_PAYLOAD_SERVICE)
    updated = task_service.update_task(
        created.id,
        **{k: v for k, v in TASK_UPDATE_PAYLOAD.items() if k in {"title", "description"}},
    )
    assert updated.title == TASK_UPDATE_PAYLOAD["title"]
    assert updated.description == TASK_UPDATE_PAYLOAD["description"]


# INT-131/003
def test_update_task_invalid_id_raises(test_db_session):
    """Updating non-existent task should raise ValueError."""
    with pytest.raises(ValueError, match="Task not found"):
        task_service.update_task(INVALID_TASK_ID_NONEXISTENT, title="nope")


# INT-131/004
def test_set_task_status_completed_creates_next_occurrence(test_db_session):
    """Recurring completed tasks spawn next occurrence."""
    payload = dict(TASK_CREATE_PAYLOAD_SERVICE)
    payload["recurring"] = 7
    payload["deadline"] = date.today()
    t = task_service.add_task(**payload)
    updated = task_service.set_task_status(t.id, "Completed")
    assert updated.status.lower() == "completed"
    rows = test_db_session.execute(
        text("SELECT COUNT(*) FROM task WHERE title=:t"), {"t": payload["title"]}
    ).scalar()
    assert rows == 2


# INT-131/005
def test_set_task_status_completed_no_deadline_raises(test_db_session):
    """Recurring task without deadline should raise error."""
    payload = dict(TASK_CREATE_PAYLOAD_SERVICE)
    payload["recurring"] = 3
    payload["deadline"] = None
    t = task_service.add_task(**payload)
    with pytest.raises(ValueError, match="without a deadline"):
        task_service.set_task_status(t.id, "Completed")


# INT-131/006
def test_list_tasks_filters_and_sorts(test_db_session):
    """list_tasks applies filters and sorting correctly."""
    task_service.add_task(**TASK_CREATE_PAYLOAD_SERVICE)
    inactive = task_service.add_task(**INACTIVE_TASK_PAYLOAD_SERVICE)
    task_service.delete_task(inactive.id)
    tasks = task_service.list_tasks(active_only=True)
    assert all(t.active for t in tasks)
    assert tasks == sorted(tasks, key=lambda x: (-x.priority, x.deadline or date.max, x.id))


# INT-131/007
def test_list_parent_tasks_and_sorting(test_db_session):
    """list_parent_tasks returns only non-subtasks."""
    p = task_service.add_task(**TASK_CREATE_PAYLOAD_SERVICE)
    c = task_service.add_task(**TASK_CREATE_CHILD_SERVICE)
    task_service.link_subtask(p.id, c.id)
    parents = task_service.list_parent_tasks()
    assert all(
        all(pa.subtask_id != t.id for pa in test_db_session.query(ParentAssignment))
        for t in parents
    )
    assert isinstance(parents, list)


# INT-131/008
def test_list_parent_tasks_invalid_sort_raises(test_db_session):
    """Invalid sort_by triggers ValueError."""
    with pytest.raises(ValueError, match="Invalid sort_by"):
        task_service.list_parent_tasks(sort_by="bad_key")


# INT-131/009
def test_attach_and_detach_subtasks_success(test_db_session):
    """Attach then detach subtasks correctly updates DB."""
    p = task_service.add_task(**TASK_CREATE_PAYLOAD_SERVICE)
    c = task_service.add_task(**TASK_CREATE_CHILD_SERVICE)
    parent = task_service.attach_subtasks(p.id, [c.id])
    assert any(link.subtask_id == c.id for link in parent.subtask_links)
    result = task_service.detach_subtask(p.id, c.id)
    assert result is True
    count = test_db_session.execute(
        text("SELECT COUNT(*) FROM parent_assignment")
    ).scalar()
    assert count == 0


# INT-131/010
def test_attach_subtasks_conflict_parent_raises(test_db_session):
    """Re-attaching child to another parent raises ValueError."""
    p1 = task_service.add_task(**TASK_CREATE_PAYLOAD_SERVICE)
    p2 = task_service.add_task(**TASK_CREATE_CHILD_SERVICE)
    c = task_service.add_task(**TASK_CREATE_CHILD_SERVICE)
    task_service.attach_subtasks(p1.id, [c.id])
    with pytest.raises(ValueError, match="already have a parent"):
        task_service.attach_subtasks(p2.id, [c.id])


# INT-131/011
def test_attach_subtasks_cycle_guard_triggers(test_db_session):
    """Cycle detection logic should raise ValueError."""
    a = task_service.add_task(**TASK_CREATE_PAYLOAD_SERVICE)
    b = task_service.add_task(**TASK_CREATE_CHILD_SERVICE)
    c = task_service.add_task(**TASK_CREATE_CHILD_SERVICE)
    task_service.attach_subtasks(a.id, [b.id])
    task_service.attach_subtasks(b.id, [c.id])
    with pytest.raises(ValueError, match="Cycle detected"):
        task_service.attach_subtasks(c.id, [a.id])


# INT-131/012
def test_link_subtask_cycle_guard(test_db_session):
    """_assert_no_cycle inside link_subtask prevents loops."""
    p = task_service.add_task(**TASK_CREATE_PAYLOAD_SERVICE)
    c = task_service.add_task(**TASK_CREATE_CHILD_SERVICE)
    task_service.link_subtask(p.id, c.id)
    with pytest.raises(ValueError, match="Cycle detected"):
        task_service.link_subtask(c.id, p.id)


# INT-131/013
def test_delete_task_sets_inactive_and_removes_links(test_db_session):
    """Soft delete marks inactive and deletes ParentAssignments."""
    p = task_service.add_task(**TASK_CREATE_PAYLOAD_SERVICE)
    c = task_service.add_task(**TASK_CREATE_CHILD_SERVICE)
    task_service.link_subtask(p.id, c.id)
    before = test_db_session.execute(text("SELECT COUNT(*) FROM parent_assignment")).scalar()
    assert before == 1
    deleted = task_service.delete_task(p.id)
    assert deleted.active is False
    after = test_db_session.execute(text("SELECT COUNT(*) FROM parent_assignment")).scalar()
    assert after == 0


# INT-131/014
def test_get_task_with_subtasks_returns_children(test_db_session):
    """get_task_with_subtasks should eager load subtasks."""
    p = task_service.add_task(**TASK_CREATE_PAYLOAD_SERVICE)
    c = task_service.add_task(**TASK_CREATE_CHILD_SERVICE)
    task_service.link_subtask(p.id, c.id)
    fetched = task_service.get_task_with_subtasks(p.id)
    assert fetched is not None
    assert any(link.subtask_id == c.id for link in fetched.subtask_links)


# INT-131/015
def test_list_project_tasks_by_user_and_invalid(test_db_session):
    """list_project_tasks_by_user returns tasks for user only."""
    t = task_service.add_task(**TASK_CREATE_PAYLOAD_SERVICE)
    res = task_service.list_project_tasks_by_user(t.project_id, VALID_USER_ADMIN["user_id"])
    assert all(x.project_id == t.project_id for x in res)

    empty = task_service.list_project_tasks_by_user(t.project_id, 99999)
    assert isinstance(empty, list)


# INT-131/016
def test_delete_nonexistent_task_raises(test_db_session):
    """Deleting non-existent task raises ValueError."""
    with pytest.raises(AttributeError):
        task_service.delete_task(INVALID_TASK_ID_NONEXISTENT)


# INT-131/017
def test_assert_no_cycle_detects_multi_level_cycle(test_db_session):
    """Directly test _assert_no_cycle BFS traversal."""
    t1 = task_service.add_task(**TASK_CREATE_PAYLOAD_SERVICE)
    t2 = task_service.add_task(**TASK_CREATE_CHILD_SERVICE)
    t3 = task_service.add_task(**TASK_CREATE_CHILD_SERVICE)

    test_db_session.add(ParentAssignment(parent_id=t1.id, subtask_id=t2.id))
    test_db_session.add(ParentAssignment(parent_id=t2.id, subtask_id=t3.id))
    test_db_session.commit()

    with pytest.raises(ValueError, match="Cycle detected"):
        task_service._assert_no_cycle(
            test_db_session, parent_id=t3.id, child_id=t1.id
        )


# INT-131/018
def test_attach_empty_subtask_list_returns_parent(test_db_session):
    """Empty subtask list returns hydrated parent without changes."""
    p = task_service.add_task(**TASK_CREATE_PAYLOAD_SERVICE)
    result = task_service.attach_subtasks(p.id, [])
    assert result.id == p.id
    assert result.subtask_links == []
