# tests/backend/integration/task/test_task_get_api.py
from __future__ import annotations

import pytest
from datetime import date, timedelta, datetime

from backend.src.enums.task_status import TaskStatus
from tests.mock_data.task.integration_data import (
    TASK_CREATE_PAYLOAD,
    TASK_2_PAYLOAD,
    TASK_3_PAYLOAD,
    TASK_4_PAYLOAD,
    INACTIVE_TASK_PAYLOAD,
    TASK_CREATE_PARENT,
    EXPECTED_TASK_RESPONSE,
    EXPECTED_RESPONSE_FIELDS,
    INVALID_TASK_ID_NONEXISTENT,
    SORT_PARAMETERS,
    INVALID_DATA_SORT,
    FILTER_PARAMETERS,
    MULTI_DATA_FILTER,
    INVALID_DATA_FILTER,
    INVALID_DATA_FILTER_COMBI,
    FILTER_AND_SORT_QUERY,
    VALID_PROJECT_ID,
    VALID_PROJECT_ID_INACTIVE_TASK,
    TASK_CREATE_CHILD
)

def serialize_payload(payload: dict) -> dict:
    """Convert date/datetime objects in payload to ISO strings for JSON serialization."""
    def convert(value):
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        if isinstance(value, list):
            return [convert(v) for v in value]
        return value

    return {k: convert(v) for k, v in payload.items()}


# INT-002/001
def test_list_tasks_success(client, task_base_path):
    """Create several tasks and list them via API; verify count and default sorting."""
    for payload in (
        TASK_CREATE_PAYLOAD,
        TASK_2_PAYLOAD,     
        TASK_3_PAYLOAD,     
        TASK_4_PAYLOAD,    
    ):
        resp = client.post(f"{task_base_path}/", json=serialize_payload(payload))
        assert resp.status_code == 201

    response = client.get(f"{task_base_path}/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    assert len(data) == 4
    for i in range(len(data) - 1):
        assert data[i]["priority"] >= data[i + 1]["priority"]

# INT-002/002
@pytest.mark.parametrize("sort_param", SORT_PARAMETERS)
def test_list_task_with_sort(client, task_base_path, sort_param):
    """Create several tasks and list them via API; verify count and according to sorting criteria."""
    for payload in (
        TASK_CREATE_PAYLOAD,
        TASK_2_PAYLOAD,     
        TASK_3_PAYLOAD,     
        TASK_4_PAYLOAD,    
    ):
        resp = client.post(f"{task_base_path}/", json=serialize_payload(payload))
        assert resp.status_code == 201

    response = client.get(f"{task_base_path}/filter?sort_by={sort_param}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    if sort_param == "priority_desc":
        for i in range(len(data) - 1):
            assert data[i]["priority"] >= data[i + 1]["priority"]
            if data[i]["priority"] == data[i + 1]["priority"]:
                assert data[i]["deadline"] <= data[i + 1]["deadline"]

    elif sort_param == "priority_asc":
        for i in range(len(data) - 1):
            assert data[i]["priority"] <= data[i + 1]["priority"]
            if data[i]["priority"] == data[i + 1]["priority"]:
                assert data[i]["deadline"] <= data[i + 1]["deadline"]

    elif sort_param == "start_date_asc":
        for i in range(len(data) - 1):
            assert data[i]["start_date"] <= data[i + 1]["start_date"]
            if data[i]["start_date"] == data[i + 1]["start_date"]:
                assert data[i]["priority"] >= data[i + 1]["priority"]

    elif sort_param == "start_date_desc":
        for i in range(len(data) - 1):
            assert data[i]["start_date"] >= data[i + 1]["start_date"]
            if data[i]["start_date"] == data[i + 1]["start_date"]:
                assert data[i]["priority"] >= data[i + 1]["priority"]

    elif sort_param == "deadline_asc":
        for i in range(len(data) - 1):
            assert data[i]["deadline"] <= data[i + 1]["deadline"]
            if data[i]["deadline"] == data[i + 1]["deadline"]:
                assert data[i]["priority"] >= data[i + 1]["priority"]

    elif sort_param == "deadline_desc":
        for i in range(len(data) - 1):
            assert data[i]["deadline"] >= data[i + 1]["deadline"]
            if data[i]["deadline"] == data[i + 1]["deadline"]:
                assert data[i]["priority"] >= data[i + 1]["priority"]

    elif sort_param == "status":
        status_order = {
            TaskStatus.TO_DO.value: 0,
            TaskStatus.IN_PROGRESS.value: 1,
            TaskStatus.COMPLETED.value: 2,
            TaskStatus.BLOCKED.value: 3,
        }
        for i in range(len(data) - 1):
            assert status_order[data[i]["status"]] <= status_order[data[i + 1]["status"]]
            if data[i]["status"] == data[i + 1]["status"]:
                assert data[i]["priority"] >= data[i + 1]["priority"]

# INT-002/003
def test_list_task_with_invalid_sort(client, task_base_path):
    """Create several tasks and list them via API; verify count and according to sorting criteria."""
    for payload in (
        TASK_CREATE_PAYLOAD,
        TASK_2_PAYLOAD,     
        TASK_3_PAYLOAD,     
        TASK_4_PAYLOAD,    
    ):
        resp = client.post(f"{task_base_path}/", json=serialize_payload(payload))
        assert resp.status_code == 201

    response = client.get(f"{task_base_path}/filter?sort_by={INVALID_DATA_SORT}")
    assert response.status_code == 400

# INT-002/004
@pytest.mark.parametrize("filter_param", FILTER_PARAMETERS)
def test_list_task_with_one_filter(client, task_base_path, filter_param):
    """Create several tasks and list them via API; verify count and according to filter criteria."""
    for payload in (
        TASK_CREATE_PAYLOAD,
        TASK_2_PAYLOAD,     
        TASK_3_PAYLOAD,     
        TASK_4_PAYLOAD,    
    ):
        resp = client.post(f"{task_base_path}/", json=serialize_payload(payload))
        assert resp.status_code == 201

    response = client.get(f"{task_base_path}/filter?filters={filter_param}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    if "priority_range" in filter_param:
        for item in data:
            assert 3 <= item["priority"] <= 7

    elif "start_date_range" in filter_param:
        for item in data:
            start_date = datetime.strptime(item["start_date"], "%Y-%m-%d").date()
            assert date.today() - timedelta(days=10) <= start_date <= date.today()

    elif "deadline_range" in filter_param:
        for item in data:
            deadline = datetime.strptime(item["deadline"], "%Y-%m-%d").date()
            assert date.today() - timedelta(days=5) <= deadline <= date.today() + timedelta(days=8)

    elif "status" in filter_param:
        for item in data:
            assert item["status"] == TaskStatus.TO_DO.value

# INT-002/005
def test_list_task_with_multi_filter(client, task_base_path):
    """Create several tasks and list them via API; verify count and according to multi filter criteria."""
    for payload in (
        TASK_CREATE_PAYLOAD,
        TASK_2_PAYLOAD,     
        TASK_3_PAYLOAD,     
        TASK_4_PAYLOAD,    
    ):
        resp = client.post(f"{task_base_path}/", json=serialize_payload(payload))
        assert resp.status_code == 201

    response = client.get(f"{task_base_path}/filter?filters={MULTI_DATA_FILTER}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    for item in data:
        start_date = datetime.strptime(item["start_date"], "%Y-%m-%d").date()
        assert date.today() - timedelta(days=10) <= start_date <= date.today()
        deadline = datetime.strptime(item["deadline"], "%Y-%m-%d").date()
        assert date.today() - timedelta(days=5) <= deadline <= date.today() + timedelta(days=8)

# INT-002/006
def test_list_task_invalid_filter(client, task_base_path):
    """Test invalid filter return 400 Bad Request."""
    for payload in (
        TASK_CREATE_PAYLOAD,
        TASK_2_PAYLOAD,     
        TASK_3_PAYLOAD,     
        TASK_4_PAYLOAD,    
    ):
        resp = client.post(f"{task_base_path}/", json=serialize_payload(payload))
        assert resp.status_code == 201

    response = client.get(f"{task_base_path}/filter?filters={INVALID_DATA_FILTER}")
    assert response.status_code == 400

# INT-002/007
@pytest.mark.parametrize("invalid_combi", INVALID_DATA_FILTER_COMBI)
def test_list_task_invalid_filter_combi(client, task_base_path, invalid_combi):
    """Test invalid filter combinations return 400 Bad Request."""
    for payload in (
        TASK_CREATE_PAYLOAD,
        TASK_2_PAYLOAD,     
        TASK_3_PAYLOAD,     
        TASK_4_PAYLOAD,    
    ):
        resp = client.post(f"{task_base_path}/", json=serialize_payload(payload))
        assert resp.status_code == 201

    response = client.get(f"{task_base_path}/filter?filters={invalid_combi}")
    assert response.status_code == 400

# INT-002/008
@pytest.mark.parametrize("filter_param", FILTER_PARAMETERS)
def test_list_task_filter_and_sort(client, task_base_path, filter_param):
    """Test list task with filter and sort criteria."""
    for payload in (
        TASK_CREATE_PAYLOAD,
        TASK_2_PAYLOAD,     
        TASK_3_PAYLOAD,     
        TASK_4_PAYLOAD,    
    ):
        resp = client.post(f"{task_base_path}/", json=serialize_payload(payload))
        assert resp.status_code == 201

    response = client.get(f"{task_base_path}/parents?filters={filter_param}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    if "priority_range" in filter_param:
        for item in data:
            assert 3 <= item["priority"] <= 7

    elif "start_date_range" in filter_param:
        for item in data:
            start_date = datetime.strptime(item["start_date"], "%Y-%m-%d").date()
            assert date.today() - timedelta(days=10) <= start_date <= date.today()

    elif "deadline_range" in filter_param:
        for item in data:
            deadline = datetime.strptime(item["deadline"], "%Y-%m-%d").date()
            assert date.today() - timedelta(days=5) <= deadline <= date.today() + timedelta(days=8)

    elif "status" in filter_param:
        for item in data:
            assert item["status"] == TaskStatus.TO_DO.value

    response = client.get(f"{task_base_path}/parents?{FILTER_AND_SORT_QUERY}")
    assert response.status_code == 200
    data = response.json()

    status_order = {
            TaskStatus.TO_DO.value: 0,
            TaskStatus.IN_PROGRESS.value: 1,
            TaskStatus.COMPLETED.value: 2,
            TaskStatus.BLOCKED.value: 3,
        }
    for i in range(len(data) - 1):
        assert status_order[data[i]["status"]] <= status_order[data[i + 1]["status"]]
        if data[i]["status"] == data[i + 1]["status"]:
            assert data[i]["priority"] >= data[i + 1]["priority"]
    for item in data:
        assert 3 <= item["priority"] <= 7

# INT-002/009
def test_get_task_successful(client, task_base_path):
    """Retrieve a single task by ID"""
    response = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    assert response.status_code == 201
    task_id = EXPECTED_TASK_RESPONSE["id"]

    response = client.get(f"{task_base_path}/{task_id}")
    assert response.status_code == 200
    data = response.json()
    for field in EXPECTED_RESPONSE_FIELDS:
        assert field in data
    assert data["id"] == task_id
    assert data["title"] == EXPECTED_TASK_RESPONSE["title"]

# # INT-002/010
def test_get_task_not_found(client, task_base_path):
    """Retrieve task with non-existent ID returns 404"""
    response = client.get(f"{task_base_path}/{INVALID_TASK_ID_NONEXISTENT}")
    assert response.status_code == 404

# INT-002/011
def test_list_tasks_excludes_inactive(client, task_base_path):
    """Inactive tasks should not appear in list."""

    for payload in (
        TASK_CREATE_PAYLOAD,
        INACTIVE_TASK_PAYLOAD    
    ):
        resp = client.post(f"{task_base_path}/", json=serialize_payload(payload))
        assert resp.status_code == 201

    response = client.get(f"{task_base_path}/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    
# INT-002/012
def test_list_task_by_project(client, task_base_path): 
    for payload in (
        TASK_CREATE_PAYLOAD,
        TASK_2_PAYLOAD,     
        TASK_3_PAYLOAD,     
        TASK_4_PAYLOAD,
        INACTIVE_TASK_PAYLOAD    
    ):
        resp = client.post(f"{task_base_path}/", json=serialize_payload(payload))
        assert resp.status_code == 201
    
    response = client.get(f"{task_base_path}/project/{VALID_PROJECT_ID}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    response = client.get(f"{task_base_path}/project/{VALID_PROJECT_ID_INACTIVE_TASK}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

# INT-013/007
def test_list_parent_tasks_excludes_subtasks(client, task_base_path):
    """Children created with parent_id should not appear in parent list endpoint."""
    r_parent = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PARENT))
    assert r_parent.status_code == 201
    parent_id = r_parent.json()["id"]

    child_payload = dict(TASK_CREATE_CHILD)
    child_payload["parent_id"] = parent_id
    r_child = client.post(f"{task_base_path}/", json=serialize_payload(child_payload))
    assert r_child.status_code == 201
    child_id = r_child.json()["id"]

    response = client.get(f"{task_base_path}/parents")
    assert response.status_code == 200
    ids = {t["id"] for t in response.json()}
    assert parent_id in ids
    assert child_id not in ids

# INT-013/008
@pytest.mark.parametrize("sort_param", SORT_PARAMETERS)
def test_list_parent_tasks_with_sort(client, task_base_path, sort_param):
    """Create several tasks and list them via API; verify count and according to sorting criteria."""
    r_parent = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PARENT))
    assert r_parent.status_code == 201
    parent_id = r_parent.json()["id"]

    child_payload = dict(TASK_CREATE_CHILD)
    child_payload["parent_id"] = parent_id
    r_child = client.post(f"{task_base_path}/", json=serialize_payload(child_payload))
    assert r_child.status_code == 201

    response = client.get(f"{task_base_path}/parents?sort_by={sort_param}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    if sort_param == "priority_desc":
        for i in range(len(data) - 1):
            assert data[i]["priority"] >= data[i + 1]["priority"]
            if data[i]["priority"] == data[i + 1]["priority"]:
                assert data[i]["deadline"] <= data[i + 1]["deadline"]

    elif sort_param == "priority_asc":
        for i in range(len(data) - 1):
            assert data[i]["priority"] <= data[i + 1]["priority"]
            if data[i]["priority"] == data[i + 1]["priority"]:
                assert data[i]["deadline"] <= data[i + 1]["deadline"]

    elif sort_param == "start_date_asc":
        for i in range(len(data) - 1):
            assert data[i]["start_date"] <= data[i + 1]["start_date"]
            if data[i]["start_date"] == data[i + 1]["start_date"]:
                assert data[i]["priority"] >= data[i + 1]["priority"]

    elif sort_param == "start_date_desc":
        for i in range(len(data) - 1):
            assert data[i]["start_date"] >= data[i + 1]["start_date"]
            if data[i]["start_date"] == data[i + 1]["start_date"]:
                assert data[i]["priority"] >= data[i + 1]["priority"]

    elif sort_param == "deadline_asc":
        for i in range(len(data) - 1):
            assert data[i]["deadline"] <= data[i + 1]["deadline"]
            if data[i]["deadline"] == data[i + 1]["deadline"]:
                assert data[i]["priority"] >= data[i + 1]["priority"]

    elif sort_param == "deadline_desc":
        for i in range(len(data) - 1):
            assert data[i]["deadline"] >= data[i + 1]["deadline"]
            if data[i]["deadline"] == data[i + 1]["deadline"]:
                assert data[i]["priority"] >= data[i + 1]["priority"]

    elif sort_param == "status":
        status_order = {
            TaskStatus.TO_DO.value: 0,
            TaskStatus.IN_PROGRESS.value: 1,
            TaskStatus.COMPLETED.value: 2,
            TaskStatus.BLOCKED.value: 3,
        }
        for i in range(len(data) - 1):
            assert status_order[data[i]["status"]] <= status_order[data[i + 1]["status"]]
            if data[i]["status"] == data[i + 1]["status"]:
                assert data[i]["priority"] >= data[i + 1]["priority"]

# INT-013/009
def test_list_parent_tasks_invalid_sort(client, task_base_path):
    """Invalid filters on /task/parents return 400."""
    client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    response = client.get(f"{task_base_path}/parents?sort_by={INVALID_DATA_SORT}")
    assert response.status_code == 400

# INT-013/010
def test_list_parent_tasks_with_filter_and_sort(client, task_base_path):
    """GET /task/parents respects filters and sort."""
    client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    client.post(f"{task_base_path}/", json=serialize_payload(TASK_2_PAYLOAD))

    resp = client.get(f"{task_base_path}/parents?{FILTER_AND_SORT_QUERY}")
    assert resp.status_code == 200
    data = resp.json()

    status_order = {
            TaskStatus.TO_DO.value: 0,
            TaskStatus.IN_PROGRESS.value: 1,
            TaskStatus.COMPLETED.value: 2,
            TaskStatus.BLOCKED.value: 3,
        }
    
    for i in range(len(data) - 1):
        assert status_order[data[i]["status"]] <= status_order[data[i + 1]["status"]]
        if data[i]["status"] == data[i + 1]["status"]:
            assert data[i]["priority"] >= data[i + 1]["priority"]
    for item in data:
        assert 3 <= item["priority"] <= 7

# INT-013/011
@pytest.mark.parametrize("invalid_combi", INVALID_DATA_FILTER_COMBI)
def test_list_parent_tasks_invalid_filter(client, task_base_path, invalid_combi):
    """Invalid filters on /task/parents return 400."""
    client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD))
    resp = client.get(f"{task_base_path}/parents?filters={INVALID_DATA_FILTER}")
    assert resp.status_code == 400

    response = client.get(f"{task_base_path}/parents?filters={invalid_combi}")
    assert response.status_code == 400

# INT-013/012
def test_list_subtasks_success(client, task_base_path):
    """GET /task/{id}/subtasks returns correct children."""
    parent = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD)).json()
    child = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_CHILD)).json()

    client.post(f"{task_base_path}/{parent['id']}/subtasks", json={"subtask_ids": [child["id"]]})
    resp = client.get(f"{task_base_path}/{parent['id']}/subtasks")
    assert resp.status_code == 200
    data = resp.json()
    assert any(st["id"] == child["id"] for st in data)

# INT-013/013
def test_list_subtasks_empty(client, task_base_path):
    """Parent with no subtasks should return empty list."""
    parent = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD)).json()
    resp = client.get(f"{task_base_path}/{parent['id']}/subtasks")
    assert resp.status_code == 200
    assert resp.json() == []

# INT-013/014
def test_list_subtasks_nonexistent_parent(client, task_base_path):
    """Nonexistent parent id returns 404 for subtasks."""
    resp = client.get(f"{task_base_path}/{INVALID_TASK_ID_NONEXISTENT}/subtasks")
    assert resp.status_code == 404

# INT-013/015
def test_list_subtasks_inactive_parent(client, task_base_path):
    """Inactive parent should return 404 when fetching subtasks."""
    parent = client.post(f"{task_base_path}/", json=serialize_payload(TASK_CREATE_PAYLOAD)).json()
    client.post(f"{task_base_path}/{parent['id']}/delete")
    resp = client.get(f"{task_base_path}/{parent['id']}/subtasks")
    assert resp.status_code == 404