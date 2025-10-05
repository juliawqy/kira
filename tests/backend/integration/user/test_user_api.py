# tests/backend/integration/user/test_user_api.py
from copy import deepcopy

from tests.mock_data.user.unit_data import (
    VALID_USER_ADMIN,  # not used directly (kept for reference)
    VALID_USER,        # not used directly (kept for reference)
    VALID_CREATE_PAYLOAD_ADMIN,
    VALID_CREATE_PAYLOAD_USER,
    INVALID_CREATE_SHORT_PASSWORD,
    INVALID_CREATE_NO_SPECIAL,
    INVALID_CREATE_BAD_EMAIL,
    VALID_UPDATE_NAME,
    VALID_UPDATE_EMAIL,
    VALID_UPDATE_ADMIN_TOGGLE,
    VALID_PASSWORD_CHANGE,
    INVALID_PASSWORD_CHANGE_WRONG_CURRENT,
    LARGE_NAME,
    LONG_EMAIL,
    INVALID_USER_ID,
)

API_BASE = "/kira/app/api/v1/user"


def _payload(p: dict) -> dict:
    """
    Make a JSON-safe copy of a payload coming from your mock data:
    - Convert UserRole enums to their .value (string)
    """
    d = deepcopy(p)
    if "role" in d and hasattr(d["role"], "value"):
        d["role"] = d["role"].value
    return d


# -----------------------------
# Create
# -----------------------------

def test_create_user_success_admin(client):
    res = client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_ADMIN))
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["user_id"] > 0
    assert body["email"] == VALID_CREATE_PAYLOAD_ADMIN["email"]
    assert body["admin"] is True
    assert body["role"].lower() == VALID_CREATE_PAYLOAD_ADMIN["role"].value


def test_create_user_success_employee(client):
    res = client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_USER))
    assert res.status_code == 201
    body = res.json()
    assert body["user_id"] > 0
    assert body["email"] == VALID_CREATE_PAYLOAD_USER["email"]
    assert body["admin"] is False
    assert body["role"].lower() == VALID_CREATE_PAYLOAD_USER["role"].value


def test_create_user_failure_duplicate_email_400(client):
    client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_USER))
    res = client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_USER))
    assert res.status_code == 400
    assert "detail" in res.json()


def test_create_user_invalid_email_422(client):
    # Pydantic should reject bad email before hitting service
    res = client.post(f"{API_BASE}/", json=_payload(INVALID_CREATE_BAD_EMAIL))
    assert res.status_code == 422


def test_create_user_short_password_400(client):
    res = client.post(f"{API_BASE}/", json=_payload(INVALID_CREATE_SHORT_PASSWORD))
    assert res.status_code == 400
    assert "detail" in res.json()


def test_create_user_no_special_password_400(client):
    res = client.post(f"{API_BASE}/", json=_payload(INVALID_CREATE_NO_SPECIAL))
    assert res.status_code == 400
    assert "detail" in res.json()


def test_create_user_invalid_role_string_400(client):
    bad = _payload(VALID_CREATE_PAYLOAD_USER)
    bad["email"] = "bad.role@example.com"
    bad["role"] = "not_a_role"
    res = client.post(f"{API_BASE}/", json=bad)
    assert res.status_code == 400
    assert "Invalid role" in res.json()["detail"]


# -----------------------------
# Read
# -----------------------------

def test_get_user_by_id_success(client):
    created = client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_ADMIN)).json()
    uid = created["user_id"]
    res = client.get(f"{API_BASE}/{uid}")
    assert res.status_code == 200
    assert res.json()["email"] == VALID_CREATE_PAYLOAD_ADMIN["email"]


def test_get_user_by_email_success(client):
    client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_USER))
    res = client.get(f"{API_BASE}/{VALID_CREATE_PAYLOAD_USER['email']}")
    assert res.status_code == 200
    assert res.json()["email"] == VALID_CREATE_PAYLOAD_USER["email"]


def test_get_user_by_name_success(client):
    payload = _payload(VALID_CREATE_PAYLOAD_USER)
    payload["email"] = "lookup.byname@example.com"
    payload["name"] = "Lookup Name"
    created = client.post(f"{API_BASE}/", json=payload).json()
    uid = created["user_id"]
    res = client.get(f"{API_BASE}/{payload['name']}")
    assert res.status_code == 200
    assert res.json()["user_id"] == uid


def test_get_user_not_found_404(client):
    res = client.get(f"{API_BASE}/{INVALID_USER_ID}")
    assert res.status_code == 404
    assert res.json()["detail"] == "User not found"


def test_list_users_success(client):
    client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_ADMIN))
    client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_USER))
    res = client.get(f"{API_BASE}/")
    assert res.status_code == 200
    emails = {u["email"] for u in res.json()}
    assert VALID_CREATE_PAYLOAD_ADMIN["email"] in emails
    assert VALID_CREATE_PAYLOAD_USER["email"] in emails


# -----------------------------
# Update (PATCH)
# -----------------------------

def test_update_user_name_success(client):
    created = client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_USER)).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=VALID_UPDATE_NAME)
    assert res.status_code == 200
    assert res.json()["name"] == VALID_UPDATE_NAME["name"]


def test_update_user_email_success(client):
    created = client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_USER)).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=VALID_UPDATE_EMAIL)
    assert res.status_code == 200
    assert res.json()["email"] == VALID_UPDATE_EMAIL["email"]


def test_update_user_admin_toggle_success(client):
    created = client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_ADMIN)).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=VALID_UPDATE_ADMIN_TOGGLE)
    assert res.status_code == 200
    assert res.json()["admin"] == VALID_UPDATE_ADMIN_TOGGLE["admin"]


def test_update_user_invalid_role_400(client):
    created = client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_USER)).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json={"role": "bad_role"})
    assert res.status_code == 400
    assert "Invalid role" in res.json()["detail"]


def test_update_user_not_found_404(client):
    res = client.patch(f"{API_BASE}/{INVALID_USER_ID}", json=VALID_UPDATE_NAME)
    assert res.status_code == 404
    assert res.json()["detail"] == "User not found"


# -----------------------------
# Delete
# -----------------------------

def test_delete_user_success_true(client):
    created = client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_ADMIN)).json()
    uid = created["user_id"]
    res = client.delete(f"{API_BASE}/{uid}")
    assert res.status_code == 200
    assert res.json() is True


def test_delete_user_not_found_404(client):
    res = client.delete(f"{API_BASE}/{INVALID_USER_ID}")
    assert res.status_code == 404
    assert res.json()["detail"] == "User not found"


# -----------------------------
# Change Password
# -----------------------------

def test_change_password_success_true(client):
    created = client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_ADMIN)).json()
    uid = created["user_id"]
    res = client.post(f"{API_BASE}/{uid}/password", json=VALID_PASSWORD_CHANGE)
    assert res.status_code == 200
    assert res.json() is True


def test_change_password_wrong_current_403(client):
    created = client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_USER)).json()
    uid = created["user_id"]
    res = client.post(f"{API_BASE}/{uid}/password", json=INVALID_PASSWORD_CHANGE_WRONG_CURRENT)
    assert res.status_code == 403
    assert "Current password is incorrect" in res.json()["detail"]


def test_change_password_user_not_found_400(client):
    res = client.post(f"{API_BASE}/{INVALID_USER_ID}/password", json=VALID_PASSWORD_CHANGE)
    assert res.status_code == 400


# -----------------------------
# Edge cases (optional)
# -----------------------------

def test_update_large_name_ok(client):
    created = client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_USER)).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=LARGE_NAME)
    # Depending on schema constraints, this might be 200 or 400
    assert res.status_code in (200, 400)


def test_update_long_email_format_validation(client):
    created = client.post(f"{API_BASE}/", json=_payload(VALID_CREATE_PAYLOAD_USER)).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=LONG_EMAIL)
    # If EmailStr validation triggers: 422; else service might return 400
    assert res.status_code in (422, 400)
