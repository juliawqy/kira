# # tests/backend/integration/task/test_task_update_api.py

# import pytest
# from datetime import date, timedelta
# from backend.src.enums.task_status import TaskStatus

# from tests.mock_data.task.integration_data import (
#     TASK_CREATE_PAYLOAD,
#     TASK_UPDATE_BASIC,
#     TASK_UPDATE_PARTIAL_TITLE_ONLY,
#     TASK_UPDATE_PARTIAL_PRIORITY,
#     TASK_UPDATE_PARTIAL_DATES,
#     TASK_UPDATE_INVALID_PRIORITY_LOW,
#     TASK_UPDATE_INVALID_PRIORITY_HIGH,
#     TASK_UPDATE_INVALID_PRIORITY_TYPE,
#     TASK_UPDATE_INVALID_DATE_FORMAT,
#     TASK_UPDATE_EMPTY_TITLE,
#     TASK_UPDATE_LONG_TEXT,
#     TASK_UPDATE_PRIORITY_MIN,
#     TASK_UPDATE_PRIORITY_MAX,
#     EXPECTED_TASK_FULL_RESPONSE,
#     INVALID_TASK_ID_NONEXISTENT,
#     VALID_PROJECT_ID_INACTIVE_TASK,
#     INACTIVE_PARENT_TASK,
# )

# pytestmark = pytest.mark.integration


# # INT-003/001
# def test_update_task_full_success(client, task_base_path):

#     create_resp = client.post(f"{task_base_path}/", json=TASK_CREATE_PAYLOAD)
#     assert create_resp.status_code == 201
#     task_id = create_resp.json()["id"]

#     update_resp = client.patch(f"{task_base_path}/{task_id}", json=TASK_UPDATE_BASIC)
#     assert update_resp.status_code == 200
#     data = update_resp.json()
#     assert data["title"] == TASK_UPDATE_BASIC["title"]
#     assert data["priority"] == TASK_UPDATE_BASIC["priority"]

#     get_resp = client.get(f"{task_base_path}/{task_id}")
#     assert get_resp.status_code == 200
#     fetched = get_resp.json()
#     for field, value in TASK_UPDATE_BASIC.items():
#         assert fetched[field] == value


# # INT-003/002
# @pytest.mark.parametrize(
#     "payload,expected_fields",
#     [
#         (TASK_UPDATE_PARTIAL_TITLE_ONLY, ["title"]),
#         (TASK_UPDATE_PARTIAL_PRIORITY, ["priority"]),
#         (TASK_UPDATE_PARTIAL_DATES, ["start_date", "deadline"]),
#     ],
# )
# def test_update_task_partial_fields(client, task_base_path, payload, expected_fields):
#     create_resp = client.post(f"{task_base_path}/", json=TASK_CREATE_PAYLOAD)
#     assert create_resp.status_code == 201
#     task_id = create_resp.json()["id"]

#     update_resp = client.patch(f"{task_base_path}/{task_id}", json=payload)
#     assert update_resp.status_code == 200
#     data = update_resp.json()
#     for field in expected_fields:
#         assert data[field] == payload[field]


# # INT-003/004
# @pytest.mark.parametrize(
#     "payload",
#     [
#         TASK_UPDATE_INVALID_PRIORITY_LOW,
#         TASK_UPDATE_INVALID_PRIORITY_HIGH,
#         TASK_UPDATE_INVALID_PRIORITY_TYPE,
#         TASK_UPDATE_INVALID_DATE_FORMAT
#     ],
# )
# def test_invalid_updates(client, task_base_path, payload):
#     create_resp = client.post(f"{task_base_path}/", json=TASK_CREATE_PAYLOAD)
#     task_id = create_resp.json()["id"]

#     resp = client.patch(f"{task_base_path}/{task_id}", json=payload)
#     assert resp.status_code == 422


# # INT-003/005
# @pytest.mark.parametrize(
#     "task_id_override, expected_status",
#     [(INVALID_TASK_ID_NONEXISTENT, 404)],
# )
# def test_update_nonexistent_or_inactive_task(client, task_base_path, task_id_override, expected_status):
#     create_resp = client.post(f"{task_base_path}/", json=TASK_CREATE_PAYLOAD)
#     assert create_resp.status_code == 201

#     resp = client.patch(f"{task_base_path}/{task_id_override}", json=TASK_UPDATE_BASIC)
#     assert resp.status_code == expected_status


# # INT-003/006
# @pytest.mark.parametrize(
#     "payload,expected_priority",
#     [   
#         (TASK_UPDATE_PRIORITY_MIN, 1),
#         (TASK_UPDATE_PRIORITY_MAX, 10),
#     ],
# )
# def test_update_priority_boundaries(client, task_base_path, payload, expected_priority):
#     """
#     INT-003/006
#     Verify that priority boundary values (1, 10) are accepted.
#     """
#     create_resp = client.post(f"{task_base_path}/", json=TASK_CREATE_PAYLOAD)
#     task_id = create_resp.json()["id"]

#     update_resp = client.patch(f"{task_base_path}/{task_id}", json=payload)
#     assert update_resp.status_code == 200
#     assert update_resp.json()["priority"] == expected_priority

# # INT-003/007
# def test_update_long_text_fields(client, task_base_path):

#     create_resp = client.post(f"{task_base_path}/", json=TASK_CREATE_PAYLOAD)
#     task_id = create_resp.json()["id"]

#     resp = client.patch(f"{task_base_path}/{task_id}", json=TASK_UPDATE_LONG_TEXT)
#     assert resp.status_code == 200
#     data = resp.json()
#     assert len(data["title"]) == len(TASK_UPDATE_LONG_TEXT["title"])
#     assert len(data["description"]) == len(TASK_UPDATE_LONG_TEXT["description"])


# # INT-022/001
# def test_transition_to_in_progress(client, task_base_path):
#     create_resp = client.post(f"{task_base_path}/", json=TASK_CREATE_PAYLOAD)
#     task_id = create_resp.json()["id"]

#     start_resp = client.post(f"{task_base_path}/{task_id}/status/{TaskStatus.IN_PROGRESS.value}")
#     assert start_resp.status_code == 200
#     assert start_resp.json()["status"] == TaskStatus.IN_PROGRESS.value

# # INT-022/002
# def test_transition_to_completed(client, task_base_path):
#     task = TASK_CREATE_PAYLOAD.copy()
#     task["status"] = TaskStatus.IN_PROGRESS.value
#     create_resp = client.post(f"{task_base_path}/", json=task)
#     task_id = create_resp.json()["id"]

#     complete_resp = client.post(f"{task_base_path}/{task_id}/status/{TaskStatus.COMPLETED.value}")
#     assert complete_resp.status_code == 200
#     assert complete_resp.json()["status"] == TaskStatus.COMPLETED.value

# # INT-022/003
# def test_transition_to_blocked(client, task_base_path):

#     task = TASK_CREATE_PAYLOAD.copy()
#     task["status"] = TaskStatus.IN_PROGRESS.value
#     create_resp = client.post(f"{task_base_path}/", json=task)
#     task_id = create_resp.json()["id"]

#     block_resp = client.post(f"{task_base_path}/{task_id}/status/{TaskStatus.BLOCKED.value}")
#     assert block_resp.status_code == 200
#     assert block_resp.json()["status"] == TaskStatus.BLOCKED.value
