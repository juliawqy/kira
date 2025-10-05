# tests/backend/unit/task/test_task_add.py
from __future__ import annotations

from datetime import date, timedelta
import pytest

import backend.src.services.task as svc
from backend.src.services.task import TaskStatus

pytestmark = pytest.mark.unit

# UNI-048/001
def test_add_task_minimal_requires_bucket_and_sets_defaults():
    """Create with minimal fields (+ required priority_bucket); verify defaults and persistence."""
    t = svc.add_task(
        title="Minimal",
        description=None,
        start_date=None,
        deadline=None,
        priority_bucket=5,  # required on creation
    )
    assert hasattr(t, "id") and isinstance(t.id, int)
    assert t.status == TaskStatus.TO_DO.value
    assert t.priority_bucket == 5
    assert t.active is True
    assert t.project_id is None

    got = svc.get_task_with_subtasks(t.id)
    assert got is not None
    assert got.title == "Minimal"
    assert got.subtasks == []

# UNI-048/002
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
        priority_bucket=9,
        project_id=123,
        active=False,
    )
    got = svc.get_task_with_subtasks(t.id)
    assert got is not None
    assert (got.title, got.description, got.start_date, got.deadline) == ("Full", "desc", start, due)
    assert (got.status, got.priority_bucket, got.project_id, got.active) == (
        TaskStatus.IN_PROGRESS.value, 9, 123, False
    )

# UNI-048/003
def test_add_task_with_parent_links_child_to_parent():
    """Create child with parent_id; parent lists child."""
    parent = svc.add_task(title="Parent", description=None, start_date=None, deadline=None, priority_bucket=6)
    child = svc.add_task(title="Child-1", description=None, start_date=None, deadline=None, priority_bucket=4, parent_id=parent.id)

    got_parent = svc.get_task_with_subtasks(parent.id)
    assert [st.title for st in got_parent.subtasks] == ["Child-1"]
    assert any(st.id == child.id for st in got_parent.subtasks)


# UNI-048/004
def test_add_multiple_children_under_same_parent():
    """Attach multiple children at creation; all links persist."""
    parent = svc.add_task(title="Parent-X", description=None, start_date=None, deadline=None, priority_bucket=5)
    c1 = svc.add_task(title="C1", description=None, start_date=None, deadline=None, priority_bucket=4, parent_id=parent.id)
    c2 = svc.add_task(title="C2", description=None, start_date=None, deadline=None, priority_bucket=7, parent_id=parent.id)

    got_parent = svc.get_task_with_subtasks(parent.id)
    assert {st.title for st in got_parent.subtasks} == {"C1", "C2"}
    assert any(st.id == c1.id for st in got_parent.subtasks)
    assert any(st.id == c2.id for st in got_parent.subtasks)


# UNI-048/005
def test_add_task_with_inactive_parent_raises_value_error():
    """Reject linking to an inactive parent."""
    parent = svc.add_task(title="P", description=None, start_date=None, deadline=None, priority_bucket=5)
    svc.archive_task(parent.id)  # parent.active -> False
    with pytest.raises(ValueError) as exc:
        svc.add_task(title="C", description=None, start_date=None, deadline=None, priority_bucket=5, parent_id=parent.id)
    assert "inactive" in str(exc.value)



# UNI-048/006
def test_add_task_with_nonexistent_parent_raises_value_error():
    """Reject non-existent parent_id with a helpful error."""
    with pytest.raises(ValueError) as exc:
        svc.add_task(
            title="Orphan",
            description=None,
            start_date=None,
            deadline=None,
            priority_bucket=5,
            parent_id=999_999,
        )
    # allow either exact message or a substring depending on your service text
    assert "not found" in str(exc.value)


# UNI-048/007
@pytest.mark.parametrize("bad_bucket", [-1, 0, 11, 999])
def test_add_task_with_invalid_priority_bucket_raises_value_error(bad_bucket: int):
    """Reject invalid priority_bucket (allowed: 1..10)."""
    with pytest.raises(ValueError) as exc:
        svc.add_task(
            title="BadBucket",
            description=None,
            start_date=None,
            deadline=None,
            priority_bucket=bad_bucket,  # out of range
        )
    assert "priority_bucket" in str(exc.value) or "between 1 and 10" in str(exc.value)


# UNI-048/008
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
            priority_bucket=5,
        )
    assert "Invalid status" in str(exc.value)


# UNI-048/009
@pytest.mark.parametrize("bad_parent", [0, -1])
def test_add_task_with_invalid_parent_sentinel_values_raises(bad_parent: int):
    """Reject impossible parent ids (0/negative)."""
    with pytest.raises(ValueError) as exc:
        svc.add_task(
            title="X",
            description=None,
            start_date=None,
            deadline=None,
            priority_bucket=5,
            parent_id=bad_parent,
        )
    assert "not found" in str(exc.value)
