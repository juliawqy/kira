# tests/backend/unit/task/test_task_attach_detach.py
from __future__ import annotations

import pytest
import backend.src.services.task as svc

pytestmark = pytest.mark.unit


def _mk(title: str, priority_bucket: int = 5, active: bool = True):
    """Helper to create a task with required priority_bucket quickly."""
    t = svc.add_task(
        title=title,
        description=None,
        start_date=None,
        deadline=None,
        priority_bucket=priority_bucket,
        active=active,
    )
    return t


def test_attach_subtasks_happy_path():
    """Attach two children; parent returns both."""
    p = _mk("P")
    c1 = _mk("C1")
    c2 = _mk("C2")

    parent = svc.attach_subtasks(p.id, [c1.id, c2.id])
    titles = {t.title for t in parent.subtasks}
    assert titles == {"C1", "C2"}


def test_attach_subtasks_idempotent():
    """Re-attaching same child is a no-op (no duplicates)."""
    p = _mk("P")
    c1 = _mk("C1")

    svc.attach_subtasks(p.id, [c1.id])
    again = svc.attach_subtasks(p.id, [c1.id])  # no error, no dup
    titles = [t.title for t in again.subtasks]
    assert set(titles) == {"C1"}
    assert len(titles) == 1


def test_attach_subtasks_parent_not_found():
    """Missing parent -> ValueError."""
    c1 = _mk("C1")
    with pytest.raises(ValueError, match=r"Parent task .* not found"):
        svc.attach_subtasks(999_999, [c1.id])


def test_attach_subtasks_inactive_parent():
    """Inactive parent cannot accept subtasks."""
    p = _mk("P")
    c = _mk("C")
    svc.archive_task(p.id)  # active -> False
    with pytest.raises(ValueError, match=r"inactive"):
        svc.attach_subtasks(p.id, [c.id])


def test_attach_subtasks_missing_child():
    """Unknown child id -> ValueError."""
    p = _mk("P")
    with pytest.raises(ValueError, match=r"not found"):
        svc.attach_subtasks(p.id, [123_456])


def test_attach_subtasks_inactive_child():
    """Inactive child cannot be attached."""
    p = _mk("P")
    c = _mk("C")
    svc.archive_task(c.id)
    with pytest.raises(ValueError, match=r"inactive"):
        svc.attach_subtasks(p.id, [c.id])


def test_attach_subtasks_self_link():
    """Parent cannot be its own child."""
    p = _mk("P")
    with pytest.raises(ValueError, match=r"own parent"):
        svc.attach_subtasks(p.id, [p.id])


def test_attach_subtasks_conflict_existing_parent():
    """Child already linked to another parent -> conflict."""
    p1 = _mk("P1")
    p2 = _mk("P2")
    c = _mk("C")
    svc.attach_subtasks(p1.id, [c.id])
    with pytest.raises(ValueError, match=r"already (has|have) a parent"):
        svc.attach_subtasks(p2.id, [c.id])


def test_attach_subtasks_cycle_detection():
    """Prevent cycles: A->B exists; attaching B->A should fail."""
    a = _mk("A")
    b = _mk("B")
    svc.attach_subtasks(a.id, [b.id])
    with pytest.raises(ValueError, match=r"cycle|Cycle"):
        svc.attach_subtasks(b.id, [a.id])


def test_attach_subtasks_all_or_nothing():
    """If one id is invalid, none are attached."""
    p = _mk("P")
    c = _mk("C")
    with pytest.raises(ValueError, match=r"not found"):
        svc.attach_subtasks(p.id, [c.id, 999_999])
    # verify no links created
    got = svc.get_task_with_subtasks(p.id)
    assert got.subtasks == []


def test_detach_subtask_happy():
    """Detach existing link -> True and link removed."""
    p = _mk("P")
    c = _mk("C")
    svc.attach_subtasks(p.id, [c.id])

    ok = svc.detach_subtask(p.id, c.id)
    assert ok is True
    got = svc.get_task_with_subtasks(p.id)
    assert got.subtasks == []


def test_detach_subtask_missing_link():
    """Missing link -> ValueError."""
    p = _mk("P")
    c = _mk("C")
    with pytest.raises(ValueError, match=r"Link not found|not found"):
        svc.detach_subtask(p.id, c.id)


def test_attach_subtasks_cycle_detection_long_chain():
    """A->B, B->C; attaching C->A must be rejected (deep traversal)."""
    a = _mk("A")
    b = _mk("B")
    c = _mk("C")

    svc.attach_subtasks(a.id, [b.id])
    svc.attach_subtasks(b.id, [c.id])

    with pytest.raises(ValueError, match=r"cycle|Cycle"):
        svc.attach_subtasks(c.id, [a.id])
