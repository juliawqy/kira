# tests/backend/unit/task/test_task_delete.py
from __future__ import annotations

import pytest
import backend.src.services.task as svc

pytestmark = pytest.mark.unit


def _mk(title: str, *, priority_bucket: int = 5, parent_id: int | None = None):
    """Helper to create a task with required priority_bucket."""
    return svc.add_task(
        title=title,
        description=None,
        start_date=None,
        deadline=None,
        priority_bucket=priority_bucket,
        parent_id=parent_id,
    )


def test_archive_parent_detaches_children_by_default():
    """Archiving a parent detaches links; children become top-level parents."""
    p = _mk("P")
    c = _mk("C", parent_id=p.id)

    updated = svc.archive_task(p.id)  # detach_links=True by default
    assert updated.active is False

    # Parent now has no children; child floats to top level
    got_p = svc.get_task_with_subtasks(p.id)
    assert got_p.subtasks == []

    titles = {t.title for t in svc.list_parent_tasks()}  # active_only=True default
    assert "C" in titles and "P" not in titles  # P inactive, C is now parent


def test_archive_child_detaches_from_parent():
    """Archiving a child removes the link from the parent."""
    p = _mk("P")
    c = _mk("C", parent_id=p.id)

    svc.archive_task(c.id)
    got_p = svc.get_task_with_subtasks(p.id)
    assert got_p.subtasks == []

    # Archived child won't appear in parent list (active_only=True)
    titles = {t.title for t in svc.list_parent_tasks()}
    assert "C" not in titles and "P" in titles  # P still active


def test_archive_parent_without_detach_keeps_links_and_hides_both_from_default_listing():
    """If detach_links=False, parent stays linked to child; both are hidden by default list."""
    p = _mk("P")
    _c = _mk("C", parent_id=p.id)

    svc.archive_task(p.id, detach_links=False)

    # Default listing hides inactive parents; child is still linked -> not a parent
    titles = {t.title for t in svc.list_parent_tasks()}  # active_only=True default
    assert titles == set()  # neither P nor C shows up

    # If we include inactive, parent appears and still has its subtask link
    titles_all = {t.title for t in svc.list_parent_tasks(active_only=False)}
    assert "P" in titles_all

    got_p = svc.get_task_with_subtasks(p.id)
    assert [st.title for st in got_p.subtasks] == ["C"]


def test_restore_parent_after_default_archive_does_not_restore_links():
    """Restoring a previously archived parent does not reattach children."""
    p = _mk("P")
    c = _mk("C", parent_id=p.id)

    svc.archive_task(p.id)  # detaches by default
    restored = svc.restore_task(p.id)
    assert restored.active is True

    got_p = svc.get_task_with_subtasks(p.id)
    assert got_p.subtasks == []  # links not restored

    # Child remains a top-level parent
    titles = {t.title for t in svc.list_parent_tasks()}
    assert "C" in titles and "P" in titles


def test_restore_child_does_not_relink_to_parent():
    """Restoring a child archived earlier does not reattach it."""
    p = _mk("P")
    c = _mk("C", parent_id=p.id)

    svc.archive_task(c.id)
    svc.restore_task(c.id)

    got_p = svc.get_task_with_subtasks(p.id)
    assert got_p.subtasks == []  # still detached

    titles = {t.title for t in svc.list_parent_tasks()}
    assert "C" in titles and "P" in titles  # both active parents now


def test_archive_missing_task_raises_value_error():
    """Archiving a non-existent id raises ValueError."""
    with pytest.raises(ValueError):
        svc.archive_task(999_999)


def test_restore_missing_task_raises_value_error():
    """Restoring a non-existent id raises ValueError."""
    with pytest.raises(ValueError):
        svc.restore_task(999_999)


def test_archive_is_idempotent():
    """Archiving an already inactive task keeps it inactive and stable."""
    t = _mk("X")
    svc.archive_task(t.id)
    again = svc.archive_task(t.id)  # should not raise
    assert again.active is False


def test_restore_is_idempotent():
    """Restoring an already active task remains active and stable."""
    t = _mk("X")
    svc.restore_task(t.id)  # already active; should not raise
    got = svc.get_task_with_subtasks(t.id)
    assert got.active is True
