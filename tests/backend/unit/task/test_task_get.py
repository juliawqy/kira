# tests/backend/unit/task/test_task_get.py
from __future__ import annotations

from datetime import date, timedelta
import pytest

import backend.src.services.task as svc

pytestmark = pytest.mark.unit


def _mk(
    title: str,
    *,
    priority: int = 5,
    parent_id: int | None = None,
    project_id: int | None = None,
    start_date: date | None = None,
    deadline: date | None = None,
    active: bool = True,
):
    """Helper to create a task with required priority and common fields."""
    return svc.add_task(
        title=title,
        description=None,
        start_date=start_date,
        deadline=deadline,
        priority=priority,
        project_id=project_id,
        active=active,
        parent_id=parent_id,
    )

# UNI-048/032
def test_get_task_with_subtasks_nonexistent_returns_none():
    """get_task_with_subtasks returns None for unknown id."""
    assert svc.get_task_with_subtasks(999_999) is None

# UNI-048/033
def test_get_task_with_subtasks_no_children_returns_empty_list():
    """A leaf task returns an empty subtasks list."""
    t = _mk("Leaf")
    got = svc.get_task_with_subtasks(t.id)
    assert got is not None
    assert got.title == "Leaf"
    assert got.subtasks == []

# UNI-048/034
def test_get_task_with_subtasks_direct_children_only():
    """A’s subtasks include only B (direct), not grandchild C."""
    a = _mk("A")
    b = _mk("B", parent_id=a.id)
    c = _mk("C", parent_id=b.id)

    got_a = svc.get_task_with_subtasks(a.id)
    got_b = svc.get_task_with_subtasks(b.id)
    got_c = svc.get_task_with_subtasks(c.id)

    assert [st.title for st in got_a.subtasks] == ["B"]
    assert [st.title for st in got_b.subtasks] == ["C"]
    assert got_c.subtasks == []

# UNI-048/035
def test_list_parent_tasks_excludes_children():
    """Children never appear in list_parent_tasks (only top-level parents)."""
    p1 = _mk("P1")
    p2 = _mk("P2")
    _c = _mk("C2-1", parent_id=p2.id)

    parents = svc.list_parent_tasks()
    titles = {t.title for t in parents}
    assert "P1" in titles and "P2" in titles and "C2-1" not in titles

# UNI-048/036
def test_list_parent_tasks_active_only_default():
    """Inactive parents are excluded by default (active_only=True)."""
    active_p = _mk("ActiveP")
    inactive_p = _mk("InactiveP")
    svc.archive_task(inactive_p.id)

    titles = {t.title for t in svc.list_parent_tasks()}
    assert "ActiveP" in titles and "InactiveP" not in titles

# UNI-048/037
def test_list_parent_tasks_including_inactive_when_requested():
    """active_only=False includes inactive parents."""
    p1 = _mk("A1")
    p2 = _mk("A2")
    svc.archive_task(p2.id)

    titles = {t.title for t in svc.list_parent_tasks(active_only=False)}
    assert {"A1", "A2"} <= titles

# UNI-048/038
def test_list_parent_tasks_project_filter():
    """Filter by project_id returns only matching parents."""
    p10 = _mk("P10", project_id=10)
    _c10 = _mk("C10", parent_id=p10.id, project_id=10)
    _p20 = _mk("P20", project_id=20)

    titles = [t.title for t in svc.list_parent_tasks(project_id=10)]
    assert titles == ["P10"]

# UNI-048/039
def test_list_parent_tasks_ordering_deadline_then_id():
    """
    Order by deadline (earliest first, NULLs last), then id ascending for ties.
    """
    today = date.today()
    # Earliest deadlines first
    p1 = _mk("P1", deadline=today + timedelta(days=1))
    p2 = _mk("P2", deadline=today + timedelta(days=2))
    # Same deadline to test id tiebreak (p2 created before p3)
    p3 = _mk("P3", deadline=today + timedelta(days=2))
    # NULL deadline goes last
    p4 = _mk("P4", deadline=None)

    ordered = svc.list_parent_tasks()
    ordered_titles = [t.title for t in ordered]

    # First should be earliest deadline
    assert ordered_titles[0] == "P1"
    # Next two share the same deadline; lower id first (p2 then p3)
    idx_p2 = ordered_titles.index("P2")
    idx_p3 = ordered_titles.index("P3")
    assert idx_p2 < idx_p3
    # Last is the NULL deadline
    assert ordered_titles[-1] == "P4"

# UNI-048/040
def test_get_task_with_subtasks_after_archiving_parent_detaches_children():
    """Archiving a parent with default detach removes links; children become parents."""
    parent = _mk("P")
    child = _mk("C", parent_id=parent.id)

    svc.archive_task(parent.id)  # detach_links=True by default

    # Parent has no children and is inactive
    got_parent = svc.get_task_with_subtasks(parent.id)
    assert got_parent.subtasks == []

    # Child is now a top-level parent (active)
    titles = {t.title for t in svc.list_parent_tasks()}
    assert "C" in titles and "P" not in titles
