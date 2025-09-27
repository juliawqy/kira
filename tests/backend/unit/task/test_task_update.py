from __future__ import annotations

from datetime import date, timedelta
import pytest

import backend.src.services.task as svc
from backend.src.services.task import TaskStatus

pytestmark = pytest.mark.unit


def test_update_task_changes_multiple_fields():
    """Update several fields; values should persist after re-fetch."""
    start = date.today()
    due = start + timedelta(days=3)
    t = svc.add_task(
        title="Orig",
        description="desc",
        start_date=None,
        deadline=None,
        status=TaskStatus.TO_DO.value,
        priority="Medium",
        project_id=None,
        active=True,
    )

    new_due = due
    updated = svc.update_task(
        t.id,
        title="New",
        description="desc2",
        start_date=start,
        deadline=new_due,
        priority="High",
        project_id=42,
        active=False,
    )
    assert updated is not None

    got = svc.get_task_with_subtasks(t.id)
    assert got.title == "New"
    assert got.description == "desc2"
    assert got.start_date == start
    assert got.deadline == new_due
    assert got.priority == "High"
    assert got.project_id == 42
    assert got.active is False


def test_update_task_invalid_priority_raises_value_error():
    """Reject invalid priority values."""
    t = svc.add_task(title="T", description=None, start_date=None, deadline=None)
    with pytest.raises(ValueError):
        svc.update_task(t.id, priority="Ultra")  # not in {Low, Medium, High}


def test_update_task_nonexistent_returns_none():
    """Return None when the target task id does not exist."""
    assert svc.update_task(999_999, title="X") is None


def test_update_task_no_fields_is_noop():
    """No kwargs -> no change; returns current Task as-is."""
    t = svc.add_task(title="T", description="d", start_date=None, deadline=None, priority="Medium")
    before = svc.get_task_with_subtasks(t.id)
    after = svc.update_task(t.id)  # no updates
    assert after is not None
    assert after.id == before.id
    # Re-fetch to verify nothing changed
    got = svc.get_task_with_subtasks(t.id)
    assert got.title == before.title
    assert got.description == before.description
    assert got.priority == before.priority
    assert got.active == before.active
    assert got.project_id == before.project_id
    assert got.start_date == before.start_date
    assert got.deadline == before.deadline


def test_update_task_does_not_change_status():
    """Status transitions are not handled by update_task."""
    t = svc.add_task(
        title="T",
        description=None,
        start_date=None,
        deadline=None,
        status=TaskStatus.IN_PROGRESS.value,
    )
    svc.update_task(t.id, title="T2", project_id=7)  # no status arg
    got = svc.get_task_with_subtasks(t.id)
    assert got.status == TaskStatus.IN_PROGRESS.value  # unchanged
    assert got.title == "T2"
    assert got.project_id == 7


def test_update_task_partial_fields_ok():
    """Update a subset of fields; only those should change."""
    t = svc.add_task(
        title="Alpha",
        description="keep",
        start_date=None,
        deadline=None,
        priority="Low",
        project_id=1,
        active=True,
    )
    svc.update_task(t.id, priority="Medium", active=False)  # partial update
    got = svc.get_task_with_subtasks(t.id)
    assert got.priority == "Medium"
    assert got.active is False
    # untouched fields remain the same
    assert got.title == "Alpha"
    assert got.description == "keep"
    assert got.project_id == 1


def test_update_task_ignore_none_parameters():
    """Explicit None values are ignored by guards and do not clear fields."""
    t = svc.add_task(
        title="T",
        description="desc",
        start_date=date.today(),
        deadline=None,
        priority="Medium",
    )
    # Attempt "clears" (service ignores None guards)
    svc.update_task(t.id, description=None, start_date=None, deadline=None, project_id=None, active=None)
    got = svc.get_task_with_subtasks(t.id)
    assert got.description == "desc"                # unchanged
    assert got.start_date is not None               # unchanged
    assert got.deadline is None                     # unchanged
