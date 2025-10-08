<<<<<<< HEAD
=======
# tests/backend/unit/task/test_task_status.py
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
from __future__ import annotations

import pytest
import backend.src.services.task as svc
from backend.src.services.task import TaskStatus

pytestmark = pytest.mark.unit


<<<<<<< HEAD
def test_start_task_sets_in_progress():
    """start_task sets status to In-progress."""
    t = svc.add_task(title="T", description=None, start_date=None, deadline=None)
    svc.start_task(t.id)
    got = svc.get_task_with_subtasks(t.id)
    assert got.status == TaskStatus.IN_PROGRESS.value


def test_block_task_sets_blocked():
    """block_task sets status to Blocked."""
    t = svc.add_task(title="T", description=None, start_date=None, deadline=None)
=======
def _mk(title: str = "T", priority: int = 5):
    """Helper to create a task with required priority."""
    return svc.add_task(
        title=title,
        description=None,
        start_date=None,
        deadline=None,
        priority=priority,
    )

# UNI-048/041
def test_start_task_sets_in_progress():
    """start_task sets status to In-progress."""
    t = _mk()
    svc.start_task(t.id)
    got = svc.get_task_with_subtasks(t.id)
    assert got.status == TaskStatus.IN_PROGRESS.value

# UNI-048/042
def test_block_task_sets_blocked():
    """block_task sets status to Blocked."""
    t = _mk()
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
    svc.block_task(t.id)
    got = svc.get_task_with_subtasks(t.id)
    assert got.status == TaskStatus.BLOCKED.value

<<<<<<< HEAD

def test_complete_task_sets_completed():
    """complete_task sets status to Completed."""
    t = svc.add_task(title="T", description=None, start_date=None, deadline=None)
    svc.complete_task(t.id)
    got = svc.get_task_with_subtasks(t.id)
    assert got.status == TaskStatus.COMPLETED.value


def test_repeating_same_transition_is_stable():
    """Calling the same transition repeatedly leaves status unchanged."""
    t = svc.add_task(title="T", description=None, start_date=None, deadline=None)
    svc.start_task(t.id)
    svc.start_task(t.id)
    got = svc.get_task_with_subtasks(t.id)
    assert got.status == TaskStatus.IN_PROGRESS.value


=======
# UNI-048/043
def test_complete_task_sets_completed():
    """complete_task sets status to Completed."""
    t = _mk()
    svc.complete_task(t.id)
    got = svc.get_task_with_subtasks(t.id)
    assert got.status == TaskStatus.COMPLETED.value

# UNI-048/044
def test_repeating_same_transition_is_stable():
    """Calling the same transition repeatedly leaves status unchanged."""
    t = _mk()
    svc.start_task(t.id)
    svc.start_task(t.id)  # idempotent
    got = svc.get_task_with_subtasks(t.id)
    assert got.status == TaskStatus.IN_PROGRESS.value

# UNI-048/045
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_transitions_on_missing_task_raise_value_error():
    """Transitions on a non-existent id raise ValueError."""
    with pytest.raises(ValueError):
        svc.start_task(999_999)
    with pytest.raises(ValueError):
        svc.block_task(999_999)
    with pytest.raises(ValueError):
        svc.complete_task(999_999)

<<<<<<< HEAD
def test_set_status_invalid_status_raises_valueerror():
    """Direct _set_status with a bad value raises ValueError."""
    t = svc.add_task("S", None, None, None)
    with pytest.raises(ValueError, match="Invalid status"):
        svc._set_status(t.id, "NotAStatus")  # calling the internal is fine for unit tests
=======
# UNI-048/046
def test_set_status_invalid_status_raises_valueerror():
    """Direct _set_status with a bad value raises ValueError."""
    t = _mk("S")
    with pytest.raises(ValueError, match="Invalid status"):
        # Calling the internal for unit verification is fine.
        svc._set_status(t.id, "NotAStatus")  # type: ignore[arg-type]
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
