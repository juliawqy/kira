from __future__ import annotations

import pytest
import backend.src.services.task as svc
from backend.src.services.task import TaskStatus

pytestmark = pytest.mark.unit


def test_start_task_sets_in_progress():
    """start_task sets status to In-progress."""
    t = svc.add_task(title="T", description=None, start_date=None, deadline=None)
    svc.start_task(t.id)
    got = svc.get_task_with_subtasks(t.id)
    assert got.status == TaskStatus.IN_PROGRESS.value


def test_block_task_sets_blocked():
    """block_task sets status to Blocked."""
    t = svc.add_task(title="T", description=None, start_date=None, deadline=None)
    svc.block_task(t.id)
    got = svc.get_task_with_subtasks(t.id)
    assert got.status == TaskStatus.BLOCKED.value


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


def test_transitions_on_missing_task_raise_value_error():
    """Transitions on a non-existent id raise ValueError."""
    with pytest.raises(ValueError):
        svc.start_task(999_999)
    with pytest.raises(ValueError):
        svc.block_task(999_999)
    with pytest.raises(ValueError):
        svc.complete_task(999_999)