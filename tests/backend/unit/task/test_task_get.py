from __future__ import annotations

from datetime import date, timedelta
import pytest

import backend.src.services.task as svc

pytestmark = pytest.mark.unit


def test_get_task_with_subtasks_nonexistent_returns_none():
    """get_task_with_subtasks returns None for unknown id."""
    assert svc.get_task_with_subtasks(999_999) is None


def test_get_task_with_subtasks_no_children_returns_empty_list():
    """A leaf task returns an empty subtasks list."""
    t = svc.add_task(title="Leaf", description=None, start_date=None, deadline=None)
    got = svc.get_task_with_subtasks(t.id)
    assert got is not None
    assert got.title == "Leaf"
    assert got.subtasks == []


def test_get_task_with_subtasks_direct_children_only():
    """A’s subtasks include only B (direct), not grandchild C."""
    a = svc.add_task(title="A", description=None, start_date=None, deadline=None)
    b = svc.add_task(title="B", description=None, start_date=None, deadline=None, parent_id=a.id)
    c = svc.add_task(title="C", description=None, start_date=None, deadline=None, parent_id=b.id)

    got_a = svc.get_task_with_subtasks(a.id)
    got_b = svc.get_task_with_subtasks(b.id)
    got_c = svc.get_task_with_subtasks(c.id)

    assert [st.title for st in got_a.subtasks] == ["B"]
    assert [st.title for st in got_b.subtasks] == ["C"]
    assert got_c.subtasks == []


def test_list_parent_tasks_excludes_children():
    """Children never appear in list_parent_tasks (only top-level parents)."""
    p1 = svc.add_task(title="P1", description=None, start_date=None, deadline=None)
    p2 = svc.add_task(title="P2", description=None, start_date=None, deadline=None)
    _c = svc.add_task(title="C2-1", description=None, start_date=None, deadline=None, parent_id=p2.id)

    parents = svc.list_parent_tasks()
    titles = {t.title for t in parents}
    assert "P1" in titles and "P2" in titles and "C2-1" not in titles


def test_list_parent_tasks_active_only_default():
    """Inactive parents are excluded by default (active_only=True)."""
    active_p = svc.add_task(title="ActiveP", description=None, start_date=None, deadline=None)
    inactive_p = svc.add_task(title="InactiveP", description=None, start_date=None, deadline=None)
    svc.archive_task(inactive_p.id)

    titles = {t.title for t in svc.list_parent_tasks()}
    assert "ActiveP" in titles and "InactiveP" not in titles


def test_list_parent_tasks_including_inactive_when_requested():
    """active_only=False includes inactive parents."""
    p1 = svc.add_task(title="A1", description=None, start_date=None, deadline=None)
    p2 = svc.add_task(title="A2", description=None, start_date=None, deadline=None)
    svc.archive_task(p2.id)

    titles = {t.title for t in svc.list_parent_tasks(active_only=False)}
    assert {"A1", "A2"} <= titles


def test_list_parent_tasks_project_filter():
    """Filter by project_id returns only matching parents."""
    p10 = svc.add_task(title="P10", description=None, start_date=None, deadline=None, project_id=10)
    _c10 = svc.add_task(title="C10", description=None, start_date=None, deadline=None, parent_id=p10.id, project_id=10)
    _p20 = svc.add_task(title="P20", description=None, start_date=None, deadline=None, project_id=20)

    titles = [t.title for t in svc.list_parent_tasks(project_id=10)]
    assert titles == ["P10"]


def test_list_parent_tasks_ordering_deadline_then_id():
    """Order by deadline (earliest first, NULLs last), then id ascending."""
    today = date.today()
    # Earliest deadlines first
    p1 = svc.add_task(title="P1", description=None, start_date=None, deadline=today + timedelta(days=1))
    p2 = svc.add_task(title="P2", description=None, start_date=None, deadline=today + timedelta(days=2))
    # Same deadline to test id tiebreak
    p3 = svc.add_task(title="P3", description=None, start_date=None, deadline=today + timedelta(days=2))
    # NULL deadline goes last
    p4 = svc.add_task(title="P4", description=None, start_date=None, deadline=None)

    ordered = svc.list_parent_tasks()
    ordered_titles = [t.title for t in ordered]

    # First should be earliest deadline
    assert ordered_titles[0] == "P1"
    # Next two share the same deadline; lower id first (p2 created before p3)
    idx_p2 = ordered_titles.index("P2")
    idx_p3 = ordered_titles.index("P3")
    assert idx_p2 < idx_p3
    # Last is the NULL deadline
    assert ordered_titles[-1] == "P4"


def test_get_task_with_subtasks_after_archiving_parent_detaches_children():
    """Archiving a parent with default detach removes links; children become parents."""
    parent = svc.add_task(title="P", description=None, start_date=None, deadline=None)
    child = svc.add_task(title="C", description=None, start_date=None, deadline=None, parent_id=parent.id)

    svc.archive_task(parent.id)  # detach_links=True by default

    # Parent has no children and is inactive
    got_parent = svc.get_task_with_subtasks(parent.id)
    assert got_parent.subtasks == []
    assert svc.list_parent_tasks()  # Should list top-level active parents

    # Child is now a top-level parent (active)
    titles = {t.title for t in svc.list_parent_tasks()}
    assert "C" in titles and "P" not in titles
