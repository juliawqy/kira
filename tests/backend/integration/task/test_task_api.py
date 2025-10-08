<<<<<<< HEAD
=======
# tests/backend/integration/task/test_task_api.py
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
from __future__ import annotations

from datetime import date, timedelta
import pytest

<<<<<<< HEAD
from backend.src.services.task import TaskStatus
=======
from backend.src.enums.task_status import TaskStatus
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f

pytestmark = pytest.mark.integration


def _subtasks(payload: dict):
    """Return subtasks list regardless of key style (subtasks/subTasks)."""
    return payload.get("subtasks") or payload.get("subTasks") or []

<<<<<<< HEAD

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

=======
# INT-048/001
def test_create_and_get_task(client, task_base_path):
    """Create a parent task, then GET by id."""
    payload = {
        "title": "Parent A",
        "description": "desc",
        "start_date": None,
        "deadline": None,
        "priority": 5,
        "status": TaskStatus.TO_DO.value,
        "project_id": None,
        "active": True,
        "parent_id": None,
    }
    r = client.post(f"{task_base_path}/", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["title"] == "Parent A"
    assert created["priority"] == 5

    gid = created["id"]
    r2 = client.get(f"{task_base_path}/{gid}")
    assert r2.status_code == 200, r2.text
    got = r2.json()
    assert got["id"] == gid and got["title"] == "Parent A"
    assert _subtasks(got) == []

# INT-048/002
def test_create_child_and_list_via_parent(client, task_base_path):
    """Create child with parent_id; GET parent shows child; list returns parents only."""
    p = client.post(f"{task_base_path}/", json={
        "title": "P1", "description": None, "start_date": None, "deadline": None,
        "priority": 5, "status": TaskStatus.TO_DO.value,
        "project_id": None, "active": True, "parent_id": None
    }).json()

    c = client.post(f"{task_base_path}/", json={
        "title": "C1", "description": None, "start_date": None, "deadline": None,
        "priority": 6, "status": TaskStatus.TO_DO.value,
        "project_id": None, "active": True, "parent_id": p["id"]
    }).json()
    assert "id" in p and "id" in c

    rp = client.get(f"{task_base_path}/{p['id']}")
    assert rp.status_code == 200, rp.text
    got_parent = rp.json()
    assert [t["title"] for t in _subtasks(got_parent)] == ["C1"]

>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
    rlist = client.get(f"{task_base_path}/")
    assert rlist.status_code == 200, rlist.text
    titles = [t["title"] for t in rlist.json()]
    assert "P1" in titles and "C1" not in titles

<<<<<<< HEAD

=======
# INT-048/003
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_get_nonexistent_returns_404(client, task_base_path):
    """GET /task/{id} returns 404 for unknown id."""
    r = client.get(f"{task_base_path}/999999")
    assert r.status_code == 404

<<<<<<< HEAD

=======
# INT-048/004
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_update_task_details(client, task_base_path):
    """PATCH updates fields; GET reflects changes."""
    created = client.post(f"{task_base_path}/", json={
        "title": "ToUpdate", "description": "d", "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Low", "status": TaskStatus.TO_DO.value,
=======
        "priority": 3, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": 3, "active": True, "parent_id": None
    }).json()
    tid = created["id"]
    new_deadline = (date.today() + timedelta(days=5)).isoformat()

    r2 = client.patch(f"{task_base_path}/{tid}", json={
        "title": "Updated",
<<<<<<< HEAD
        "priority": "High",
=======
        "priority": 9,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "deadline": new_deadline,
        "project_id": 7,
        "active": False
    })
    assert r2.status_code == 200, r2.text
    updated = r2.json()
    assert updated["title"] == "Updated"
<<<<<<< HEAD
    assert updated["priority"] == "High"
=======
    assert updated["priority"] == 9
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
    assert updated["project_id"] == 7
    assert updated["active"] is False
    assert updated["deadline"] == new_deadline

<<<<<<< HEAD

=======
# INT-048/005
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_status_transitions_start_block_complete(client, task_base_path):
    """POST start/block/complete endpoints flip status accordingly."""
    created = client.post(f"{task_base_path}/", json={
        "title": "StatusFlow", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
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

<<<<<<< HEAD

=======
# INT-048/006
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_archive_parent_detaches_children_by_default(client, task_base_path):
    """Archiving a parent detaches links; children become top-level parents."""
    p = client.post(f"{task_base_path}/", json={
        "title": "P", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()
    client.post(f"{task_base_path}/", json={
        "title": "C", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 6, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
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

<<<<<<< HEAD

=======
# INT-048/007
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_archive_parent_without_detach_keeps_links_and_hides_both(client, task_base_path):
    """If detach_links=False, parent stays linked to child; both hidden from default list."""
    p = client.post(f"{task_base_path}/", json={
        "title": "P2", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()
    client.post(f"{task_base_path}/", json={
        "title": "C2", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 6, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
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

<<<<<<< HEAD

=======
# INT-048/008
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_restore_parent_after_default_archive_does_not_restore_links(client, task_base_path):
    """Restoring a parent (after detach) doesn't reattach children."""
    p = client.post(f"{task_base_path}/", json={
        "title": "PR", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()
    client.post(f"{task_base_path}/", json={
        "title": "CR", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 6, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
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

<<<<<<< HEAD

=======
# INT-048/009
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_create_with_invalid_priority_and_status(client, task_base_path):
    """Invalid priority/status are rejected by schema -> 422."""
    r1 = client.post(f"{task_base_path}/", json={
        "title": "BadPri", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Ultra",  # invalid
        "status": "To-do",
=======
        "priority": 0,  # invalid (must be 1-10)
        "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    })
    assert r1.status_code == 422, r1.text

    r2 = client.post(f"{task_base_path}/", json={
        "title": "BadStat", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium",
=======
        "priority": 5,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "status": "In progress",  # invalid spelling/case vs enum
        "project_id": None, "active": True, "parent_id": None
    })
    assert r2.status_code == 422, r2.text

<<<<<<< HEAD


=======
# INT-048/010
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_create_child_with_missing_or_inactive_parent_errors(client, task_base_path):
    """Missing parent -> 404; inactive parent -> 400."""
    r_missing = client.post(f"{task_base_path}/", json={
        "title": "Orphan", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": 999999
    })
    assert r_missing.status_code == 404

    # Make an inactive parent
    p = client.post(f"{task_base_path}/", json={
        "title": "P3", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()
    client.post(f"{task_base_path}/{p['id']}/archive")

    r_inactive = client.post(f"{task_base_path}/", json={
        "title": "C3", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": p["id"]
    })
    # service raises "inactive and cannot accept subtasks" -> mapped to 400 by route
    assert r_inactive.status_code == 400

<<<<<<< HEAD
def _subs(payload: dict):
    return payload.get("subtasks") or payload.get("subTasks") or []


=======

def _subs(payload: dict):
    return payload.get("subtasks") or payload.get("subTasks") or []

# INT-048/011
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_attach_subtasks_happy_and_idempotent(client, task_base_path):
    """POST /{parent}/subtasks attaches; second call idempotent."""
    p = client.post(f"{task_base_path}/", json={
        "title": "P", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()
    c1 = client.post(f"{task_base_path}/", json={
        "title": "C1", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()

    r1 = client.post(f"{task_base_path}/{p['id']}/subtasks", json={"subtask_ids": [c1["id"]]})
    assert r1.status_code == 200, r1.text
    assert [t["title"] for t in _subs(r1.json())] == ["C1"]

    r2 = client.post(f"{task_base_path}/{p['id']}/subtasks", json={"subtask_ids": [c1["id"]]})
    assert r2.status_code == 200, r2.text
<<<<<<< HEAD
    assert [t["title"] for t in _subs(r2.json())] == ["C1"]  


=======
    assert [t["title"] for t in _subs(r2.json())] == ["C1"]

# INT-048/012
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_attach_subtasks_missing_parent_and_child(client, task_base_path):
    """Missing parent/child -> 404."""
    r = client.post(f"{task_base_path}/999999/subtasks", json={"subtask_ids": []})
    assert r.status_code == 404

    p = client.post(f"{task_base_path}/", json={
        "title": "P", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()
    r2 = client.post(f"{task_base_path}/{p['id']}/subtasks", json={"subtask_ids": [999999]})
    assert r2.status_code == 404

<<<<<<< HEAD

=======
# INT-048/013
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_attach_subtasks_inactive_parent_and_child(client, task_base_path):
    """Inactive parent or child -> 400."""
    p = client.post(f"{task_base_path}/", json={
        "title": "P", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()
    c = client.post(f"{task_base_path}/", json={
        "title": "C", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()

    # archive parent
    ap = client.post(f"{task_base_path}/{p['id']}/archive")
    assert ap.status_code == 200
    r = client.post(f"{task_base_path}/{p['id']}/subtasks", json={"subtask_ids": [c["id"]]})
    assert r.status_code == 400

    # archive child
    p2 = client.post(f"{task_base_path}/", json={
        "title": "P2", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()
    client.post(f"{task_base_path}/{c['id']}/archive")
    r2 = client.post(f"{task_base_path}/{p2['id']}/subtasks", json={"subtask_ids": [c["id"]]})
    assert r2.status_code == 400

<<<<<<< HEAD

=======
# INT-048/014
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_attach_subtasks_conflict_and_cycle_and_selflink(client, task_base_path):
    """409 for conflict/cycle; 400 for self-link."""
    p1 = client.post(f"{task_base_path}/", json={
        "title": "P1", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()
    p2 = client.post(f"{task_base_path}/", json={
        "title": "P2", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()
    c = client.post(f"{task_base_path}/", json={
        "title": "C", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()

    # conflict: child already owned by p1
    client.post(f"{task_base_path}/{p1['id']}/subtasks", json={"subtask_ids": [c["id"]]})
    r_conf = client.post(f"{task_base_path}/{p2['id']}/subtasks", json={"subtask_ids": [c["id"]]})
    assert r_conf.status_code == 409

    # cycle: create p1->p2 then try p2->p1
    client.post(f"{task_base_path}/{p1['id']}/subtasks", json={"subtask_ids": [p2["id"]]})
    r_cycle = client.post(f"{task_base_path}/{p2['id']}/subtasks", json={"subtask_ids": [p1["id"]]})
    assert r_cycle.status_code == 409

    # self-link
    r_self = client.post(f"{task_base_path}/{p1['id']}/subtasks", json={"subtask_ids": [p1["id"]]})
    assert r_self.status_code == 400

<<<<<<< HEAD

=======
# INT-048/015
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_attach_subtasks_empty_list_is_ok(client, task_base_path):
    """Empty list is a no-op; returns parent with current subtasks."""
    p = client.post(f"{task_base_path}/", json={
        "title": "P", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()
    r = client.post(f"{task_base_path}/{p['id']}/subtasks", json={"subtask_ids": []})
    assert r.status_code == 200, r.text
    assert _subs(r.json()) == []

<<<<<<< HEAD

=======
# INT-048/016
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_detach_subtask_happy_and_missing(client, task_base_path):
    """DELETE link -> 204; deleting a non-existent link -> 404."""
    p = client.post(f"{task_base_path}/", json={
        "title": "P", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()
    c = client.post(f"{task_base_path}/", json={
        "title": "C", "description": None, "start_date": None, "deadline": None,
<<<<<<< HEAD
        "priority": "Medium", "status": TaskStatus.TO_DO.value,
=======
        "priority": 5, "status": TaskStatus.TO_DO.value,
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
        "project_id": None, "active": True, "parent_id": None
    }).json()
    client.post(f"{task_base_path}/{p['id']}/subtasks", json={"subtask_ids": [c["id"]]})

    d = client.delete(f"{task_base_path}/{p['id']}/subtasks/{c['id']}")
    assert d.status_code == 204, d.text

    # no longer listed
    r = client.get(f"{task_base_path}/{p['id']}/subtasks")
    assert r.status_code == 200
    assert r.json() == []

    # missing link now -> 404
    d2 = client.delete(f"{task_base_path}/{p['id']}/subtasks/{c['id']}")
    assert d2.status_code == 404

<<<<<<< HEAD

=======
# INT-048/017
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_update_task_not_found(client, task_base_path):
    """PATCH /task/{id} -> 404 when task does not exist."""
    r = client.patch(f"{task_base_path}/999999", json={"title": "x"})
    assert r.status_code == 404

<<<<<<< HEAD

=======
# INT-048/018
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_start_complete_block_not_found(client, task_base_path):
    """POST start/complete/block -> 404 when task does not exist."""
    assert client.post(f"{task_base_path}/999999/start").status_code == 404
    assert client.post(f"{task_base_path}/999999/complete").status_code == 404
    assert client.post(f"{task_base_path}/999999/block").status_code == 404

<<<<<<< HEAD

=======
# INT-048/019
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_archive_restore_not_found(client, task_base_path):
    """POST archive/restore -> 404 when task does not exist."""
    assert client.post(f"{task_base_path}/999999/archive").status_code == 404
    assert client.post(f"{task_base_path}/999999/restore").status_code == 404

<<<<<<< HEAD

=======
# INT-048/020
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_list_subtasks_parent_not_found(client, task_base_path):
    """GET /task/{id}/subtasks -> 404 when parent does not exist."""
    r = client.get(f"{task_base_path}/999999/subtasks")
    assert r.status_code == 404

<<<<<<< HEAD
=======
# INT-048/021
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
def test_detach_subtask_generic_valueerror_returns_400(client, task_base_path, monkeypatch):
    """DELETE returns 400 when service raises a non-'not found' ValueError."""
    # Patch at the route module reference so the router uses it
    from backend.src.api.v1.routes import task_route

    def boom(parent_id: int, subtask_id: int) -> bool:
        raise ValueError("some other error")

    monkeypatch.setattr(task_route.task_service, "detach_subtask", boom)
    r = client.delete(f"{task_base_path}/1/subtasks/2")
<<<<<<< HEAD
    assert r.status_code == 400, r.text
=======
    assert r.status_code == 400, r.text
>>>>>>> 90732818ea271ec617266c163ded6d656b42ad1f
