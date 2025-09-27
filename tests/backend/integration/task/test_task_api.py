from __future__ import annotations

from datetime import date, timedelta
import pytest

from backend.src.services.task import TaskStatus

pytestmark = pytest.mark.integration


def _subtasks(payload: dict):
    """Return subtasks list regardless of key style (subtasks/subTasks)."""
    return payload.get("subtasks") or payload.get("subTasks") or []


def test_create_and_get_task(client, task_base_path):
    """Create a parent task, then GET by id."""
    payload = {
        "title": "Parent A",
        "description": "desc",
        "start_date": None,
        "deadline": None,
        "priority": "Medium",
        "status": TaskStatus.TO_DO.value,
        "project_id": None,
        "active": True,
        "parent_id": None,
    }
    r = client.post(f"{task_base_path}/", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["title"] == "Parent A"

    gid = created["id"]
    r2 = client.get(f"{task_base_path}/{gid}")
    assert r2.status_code == 200, r2.text
    got = r2.json()
    assert got["id"] == gid and got["title"] == "Parent A"
    assert _subtasks(got) == []


def test_create_child_and_list_via_parent(client, task_base_path):
    """Create child with parent_id; GET parent shows child; list returns parents only."""
    p = client.post(f"{task_base_path}/", json={
        "title": "P1", "description": None, "start_date": None, "deadline": None,
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
        "project_id": None, "active": True, "parent_id": None
    }).json()

    c = client.post(f"{task_base_path}/", json={
        "title": "C1", "description": None, "start_date": None, "deadline": None,
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
        "project_id": None, "active": True, "parent_id": p["id"]
    }).json()
    assert "id" in p and "id" in c

    rp = client.get(f"{task_base_path}/{p['id']}")
    assert rp.status_code == 200, rp.text
    got_parent = rp.json()
    assert [t["title"] for t in _subtasks(got_parent)] == ["C1"]

    rlist = client.get(f"{task_base_path}/")
    assert rlist.status_code == 200, rlist.text
    titles = [t["title"] for t in rlist.json()]
    assert "P1" in titles and "C1" not in titles


def test_get_nonexistent_returns_404(client, task_base_path):
    """GET /task/{id} returns 404 for unknown id."""
    r = client.get(f"{task_base_path}/999999")
    assert r.status_code == 404


def test_update_task_details(client, task_base_path):
    """PATCH updates fields; GET reflects changes."""
    created = client.post(f"{task_base_path}/", json={
        "title": "ToUpdate", "description": "d", "start_date": None, "deadline": None,
        "priority": "Low", "status": TaskStatus.TO_DO.value,
        "project_id": 3, "active": True, "parent_id": None
    }).json()
    tid = created["id"]
    new_deadline = (date.today() + timedelta(days=5)).isoformat()

    r2 = client.patch(f"{task_base_path}/{tid}", json={
        "title": "Updated",
        "priority": "High",
        "deadline": new_deadline,
        "project_id": 7,
        "active": False
    })
    assert r2.status_code == 200, r2.text
    updated = r2.json()
    assert updated["title"] == "Updated"
    assert updated["priority"] == "High"
    assert updated["project_id"] == 7
    assert updated["active"] is False
    assert updated["deadline"] == new_deadline


def test_status_transitions_start_block_complete(client, task_base_path):
    """POST start/block/complete endpoints flip status accordingly."""
    created = client.post(f"{task_base_path}/", json={
        "title": "StatusFlow", "description": None, "start_date": None, "deadline": None,
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
        "project_id": None, "active": True, "parent_id": None
    }).json()
    tid = created["id"]

    r1 = client.post(f"{task_base_path}/{tid}/start")
    assert r1.status_code == 200, r1.text
    assert r1.json()["status"] == TaskStatus.IN_PROGRESS.value

    r2 = client.post(f"{task_base_path}/{tid}/block")
    assert r2.status_code == 200, r2.text
    assert r2.json()["status"] == TaskStatus.BLOCKED.value

    r3 = client.post(f"{task_base_path}/{tid}/complete")
    assert r3.status_code == 200, r3.text
    assert r3.json()["status"] == TaskStatus.COMPLETED.value


def test_archive_parent_detaches_children_by_default(client, task_base_path):
    """Archiving a parent detaches links; children become top-level parents."""
    p = client.post(f"{task_base_path}/", json={
        "title": "P", "description": None, "start_date": None, "deadline": None,
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
        "project_id": None, "active": True, "parent_id": None
    }).json()
    client.post(f"{task_base_path}/", json={
        "title": "C", "description": None, "start_date": None, "deadline": None,
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
        "project_id": None, "active": True, "parent_id": p["id"]
    })

    ra = client.post(f"{task_base_path}/{p['id']}/archive")
    assert ra.status_code == 200, ra.text
    assert ra.json()["active"] is False

    rp = client.get(f"{task_base_path}/{p['id']}")
    assert rp.status_code == 200, rp.text
    assert _subtasks(rp.json()) == []

    rlist = client.get(f"{task_base_path}/")
    titles = [t["title"] for t in rlist.json()]
    assert "C" in titles and "P" not in titles  # default list excludes inactive parents


def test_archive_parent_without_detach_keeps_links_and_hides_both(client, task_base_path):
    """If detach_links=False, parent stays linked to child; both hidden from default list."""
    p = client.post(f"{task_base_path}/", json={
        "title": "P2", "description": None, "start_date": None, "deadline": None,
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
        "project_id": None, "active": True, "parent_id": None
    }).json()
    client.post(f"{task_base_path}/", json={
        "title": "C2", "description": None, "start_date": None, "deadline": None,
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
        "project_id": None, "active": True, "parent_id": p["id"]
    })

    ra = client.post(f"{task_base_path}/{p['id']}/archive?detach_links=false")
    assert ra.status_code == 200, ra.text

    # default list: active_only=True -> neither appears
    rlist = client.get(f"{task_base_path}/")
    assert [t["title"] for t in rlist.json()] == []

    # but parent still has its subtask link if we fetch it directly
    rp = client.get(f"{task_base_path}/{p['id']}")
    assert [t["title"] for t in _subtasks(rp.json())] == ["C2"]


def test_restore_parent_after_default_archive_does_not_restore_links(client, task_base_path):
    """Restoring a parent (after detach) doesn't reattach children."""
    p = client.post(f"{task_base_path}/", json={
        "title": "PR", "description": None, "start_date": None, "deadline": None,
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
        "project_id": None, "active": True, "parent_id": None
    }).json()
    client.post(f"{task_base_path}/", json={
        "title": "CR", "description": None, "start_date": None, "deadline": None,
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
        "project_id": None, "active": True, "parent_id": p["id"]
    })

    client.post(f"{task_base_path}/{p['id']}/archive")  # detach=True default
    rr = client.post(f"{task_base_path}/{p['id']}/restore")
    assert rr.status_code == 200, rr.text
    assert rr.json()["active"] is True

    rp = client.get(f"{task_base_path}/{p['id']}")
    assert _subtasks(rp.json()) == []

    # both should be parents now (active_only default)
    titles = [t["title"] for t in client.get(f"{task_base_path}/").json()]
    assert "PR" in titles and "CR" in titles


def test_create_with_invalid_priority_and_status(client, task_base_path):
    """Invalid priority/status are rejected by schema -> 422."""
    r1 = client.post(f"{task_base_path}/", json={
        "title": "BadPri", "description": None, "start_date": None, "deadline": None,
        "priority": "Ultra",  # invalid
        "status": "To-do",
        "project_id": None, "active": True, "parent_id": None
    })
    assert r1.status_code == 422, r1.text

    r2 = client.post(f"{task_base_path}/", json={
        "title": "BadStat", "description": None, "start_date": None, "deadline": None,
        "priority": "Medium",
        "status": "In progress",  # invalid spelling/case vs enum
        "project_id": None, "active": True, "parent_id": None
    })
    assert r2.status_code == 422, r2.text



def test_create_child_with_missing_or_inactive_parent_errors(client, task_base_path):
    """Missing parent -> 404; inactive parent -> 400."""
    r_missing = client.post(f"{task_base_path}/", json={
        "title": "Orphan", "description": None, "start_date": None, "deadline": None,
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
        "project_id": None, "active": True, "parent_id": 999999
    })
    assert r_missing.status_code == 404

    # Make an inactive parent
    p = client.post(f"{task_base_path}/", json={
        "title": "P3", "description": None, "start_date": None, "deadline": None,
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
        "project_id": None, "active": True, "parent_id": None
    }).json()
    client.post(f"{task_base_path}/{p['id']}/archive")

    r_inactive = client.post(f"{task_base_path}/", json={
        "title": "C3", "description": None, "start_date": None, "deadline": None,
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
        "project_id": None, "active": True, "parent_id": p["id"]
    })
    # service raises "inactive and cannot accept subtasks" -> mapped to 400 by route
    assert r_inactive.status_code == 400
