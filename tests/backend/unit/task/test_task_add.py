# tests/backend/unit/task/test_task_add.py
from __future__ import annotations

from datetime import date, timedelta
import pytest

import backend.src.services.task as svc
from backend.src.services.task import TaskStatus

pytestmark = pytest.mark.unit


def test_add_task_minimal_defaults():
    """Create with minimal fields; verify defaults and persistence."""
    t = svc.add_task(title="Minimal", description=None, start_date=None, deadline=None)
    assert hasattr(t, "id") and isinstance(t.id, int)
    assert t.status == TaskStatus.TO_DO.value
    assert t.priority == "Medium"
    assert t.active is True
    assert t.project_id is None

    got = svc.get_task_with_subtasks(t.id)
    assert got is not None
    assert got.title == "Minimal"
    assert got.subtasks == []


def test_add_task_full_fields():
    """Create with all fields; round-trip values should match."""
    start = date.today()
    due = start + timedelta(days=7)
    t = svc.add_task(
        title="Full",
        description="desc",
        start_date=start,
        deadline=due,
        status=TaskStatus.IN_PROGRESS.value,
        priority="High",
        project_id=123,
        active=False,
    )
    got = svc.get_task_with_subtasks(t.id)
    assert got is not None
    assert (got.title, got.description, got.start_date, got.deadline) == ("Full", "desc", start, due)
    assert (got.status, got.priority, got.project_id, got.active) == (
        TaskStatus.IN_PROGRESS.value, "High", 123, False
    )


def test_add_task_with_parent_links_child_to_parent():
    """Create child with parent_id; parent lists child."""
    parent = svc.add_task(title="Parent", description=None, start_date=None, deadline=None)
    child = svc.add_task(title="Child-1", description=None, start_date=None, deadline=None, parent_id=parent.id)

    got_parent = svc.get_task_with_subtasks(parent.id)
    assert [st.title for st in got_parent.subtasks] == ["Child-1"]
    # Verify link via parent’s subtasks (avoid lazy-loading child.parent)
    assert any(st.id == child.id for st in got_parent.subtasks)


def test_add_multiple_children_under_same_parent():
    """Attach multiple children at creation; all links persist."""
    parent = svc.add_task(title="Parent-X", description=None, start_date=None, deadline=None)
    c1 = svc.add_task(title="C1", description=None, start_date=None, deadline=None, parent_id=parent.id)
    c2 = svc.add_task(title="C2", description=None, start_date=None, deadline=None, parent_id=parent.id)

    got_parent = svc.get_task_with_subtasks(parent.id)
    assert {st.title for st in got_parent.subtasks} == {"C1", "C2"}
    # Verify both links via parent’s subtasks (avoid lazy-loading child.parent)
    assert any(st.id == c1.id for st in got_parent.subtasks)
    assert any(st.id == c2.id for st in got_parent.subtasks)


def test_add_task_with_nonexistent_parent_raises_value_error():
    """Reject non-existent parent_id with a helpful error."""
    with pytest.raises(ValueError) as exc:
        svc.add_task(title="Orphan", description=None, start_date=None, deadline=None, parent_id=999_999)
    assert "Parent task 999999 not found" in str(exc.value)


@pytest.mark.parametrize("bad_priority", ["VeryHigh", "", "medium", None])
def test_add_task_with_invalid_priority_raises_value_error(bad_priority):
    """Reject invalid priority (allowed: Low/Medium/High)."""
    with pytest.raises(ValueError) as exc:
        svc.add_task(
            title="BadPriority",
            description=None,
            start_date=None,
            deadline=None,
            priority=bad_priority,  # type: ignore[arg-type]
        )
    assert "Invalid priority" in str(exc.value)


@pytest.mark.parametrize("bad_status", ["In progress", "DONE", "Todo", None])
def test_add_task_with_invalid_status_raises_value_error(bad_status):
    """Reject invalid status (must match allowed strings exactly)."""
    with pytest.raises(ValueError) as exc:
        svc.add_task(
            title="BadStatus",
            description=None,
            start_date=None,
            deadline=None,
            status=bad_status,  # type: ignore[arg-type]
        )
    assert "Invalid status" in str(exc.value)


def test_add_task_with_inactive_parent_raises_value_error():
    """Reject linking to an inactive parent."""
    parent = svc.add_task(title="P", description=None, start_date=None, deadline=None)
    svc.archive_task(parent.id)  # parent.active -> False
    with pytest.raises(ValueError) as exc:
        svc.add_task(title="C", description=None, start_date=None, deadline=None, parent_id=parent.id)
    assert "inactive and cannot accept subtasks" in str(exc.value)


@pytest.mark.parametrize("bad_parent", [0, -1])
def test_add_task_with_invalid_parent_sentinel_values_raises(bad_parent: int):
    """Reject impossible parent ids (0/negative)."""
    with pytest.raises(ValueError) as exc:
        svc.add_task(title="X", description=None, start_date=None, deadline=None, parent_id=bad_parent)
    assert f"Parent task {bad_parent} not found" in str(exc.value)
