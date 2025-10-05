# tests/backend/integration/user/test_user_api.py
import os
import tempfile
import uuid
from copy import deepcopy

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.src.database.db_setup import Base
from backend.src.main import app

from tests.mock_data.user.unit_data import (
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


# ---------- helpers ----------

def _payload(p: dict) -> dict:
    """JSON-safe copy; convert UserRole enums to string values if present."""
    d = deepcopy(p)
    if "role" in d and hasattr(d["role"], "value"):
        d["role"] = d["role"].value  # e.g., "manager" / "staff"
    return d

def _with_unique_email(p: dict, tag: str = "") -> dict:
    """Return payload with a unique +tag email to avoid dupes inside a test."""
    d = _payload(p)
    local, domain = d["email"].split("@", 1)
    suffix = tag or uuid.uuid4().hex[:8]
    d["email"] = f"{local}+{suffix}@{domain}"
    return d


# ---------- per-test temp DB + SessionLocal patch + client ----------

@pytest.fixture(autouse=True)
def isolated_test_db(monkeypatch):
    """
    Brand-new SQLite DB file per test.
    Patch SessionLocal in BOTH:
      - backend.src.database.db_setup
      - backend.src.services.user
    so the service layer and the API use this DB.
    """
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    engine = create_engine(
        f"sqlite:///{db_path}",
        echo=False,
        future=True,
        connect_args={"check_same_thread": False}, 
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )

    monkeypatch.setattr("backend.src.database.db_setup.SessionLocal", TestingSessionLocal, raising=True)
    monkeypatch.setattr("backend.src.services.user.SessionLocal", TestingSessionLocal, raising=False)

    try:
        yield
    finally:
        try:
            engine.dispose()
        finally:
            try:
                os.unlink(db_path)
            except OSError:
                pass


@pytest.fixture
def client(isolated_test_db):
    """FastAPI TestClient that now writes/reads to the per-test DB."""
    with TestClient(app) as c:
        yield c

# Create
# INT-052/001
def test_create_user_success_admin(client):
    res = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_ADMIN, "create-admin"))
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["user_id"] > 0
    assert body["email"].startswith("alice.admin+create-admin@")
    expected_role = _payload(VALID_CREATE_PAYLOAD_ADMIN)["role"]
    assert body["role"].lower() == expected_role.lower()

# INT-052/002
def test_create_user_success_employee(client):
    res = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "create-emp"))
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["user_id"] > 0
    assert body["email"].startswith("bob.employee+create-emp@")
    expected_role = _payload(VALID_CREATE_PAYLOAD_USER)["role"]
    assert body["role"].lower() == expected_role.lower()

# INT-052/003
def test_create_user_short_password_returns_422(client):
    res = client.post(f"{API_BASE}/", json=_with_unique_email(INVALID_CREATE_SHORT_PASSWORD, "short"))
    assert res.status_code == 422, res.text

# INT-052/004
def test_create_user_invalid_email_returns_422(client):
    res = client.post(f"{API_BASE}/", json=_payload(INVALID_CREATE_BAD_EMAIL))
    assert res.status_code == 422, res.text

# INT-052/005
def test_create_user_no_special_password_returns_400(client):
    res = client.post(f"{API_BASE}/", json=_with_unique_email(INVALID_CREATE_NO_SPECIAL, "nospecial"))
    assert res.status_code == 400, res.text

# INT-052/006
def test_create_user_invalid_role_returns_400(client):
    bad = _with_unique_email(VALID_CREATE_PAYLOAD_USER, "badrole")
    bad["role"] = "not_a_role"
    res = client.post(f"{API_BASE}/", json=bad)
    assert res.status_code == 400, res.text
    assert "Invalid role" in res.json()["detail"]


# Read
# INT-054/001
def test_get_user_by_id_success(client):
    res = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_ADMIN, "get-by-id"))
    assert res.status_code == 201, res.text
    uid = res.json()["user_id"]

    res = client.get(f"{API_BASE}/{uid}")
    assert res.status_code == 200, res.text
    assert res.json()["user_id"] == uid

# INT-054/002
def test_get_user_by_email_success(client):
    payload = _with_unique_email(VALID_CREATE_PAYLOAD_USER, "by-email")
    assert client.post(f"{API_BASE}/", json=payload).status_code == 201
    res = client.get(f"{API_BASE}/{payload['email']}")
    assert res.status_code == 200, res.text
    assert res.json()["email"] == payload["email"]

# INT-054/003
def test_get_user_by_numeric_id_branch_and_404(client):
    res = client.get(f"{API_BASE}/999999")
    assert res.status_code == 404, res.text
    assert res.json()["detail"] == "User not found"

# INT-054/004
def test_list_users_empty(client):
    res = client.get(f"{API_BASE}/")
    assert res.status_code == 200, res.text
    assert res.json() == [] 

# INT-054/005
def test_list_users_two(client):
    p1 = _with_unique_email(VALID_CREATE_PAYLOAD_USER, "list1")
    p2 = _with_unique_email(VALID_CREATE_PAYLOAD_ADMIN, "list2")
    assert client.post(f"{API_BASE}/", json=p1).status_code == 201
    assert client.post(f"{API_BASE}/", json=p2).status_code == 201

    res = client.get(f"{API_BASE}/")
    assert res.status_code == 200, res.text
    data = res.json()
    emails = {u["email"] for u in data}
    assert p1["email"] in emails and p2["email"] in emails
    assert len(data) == 2  

# INT-054/006
def test_get_user_not_found_after_delete(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "cover-6768")).json()
    uid = created["user_id"]

    res_del = client.delete(f"{API_BASE}/{uid}")
    assert res_del.status_code == 200 and res_del.json() is True, res_del.text

    res_get = client.get(f"{API_BASE}/{uid}")
    assert res_get.status_code == 404, res_get.text
    assert res_get.json()["detail"] == "User not found"

# Update 
# INT-053/001
def test_update_user_name_success(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "upd-name")).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=VALID_UPDATE_NAME)
    assert res.status_code == 200, res.text
    assert res.json()["name"] == VALID_UPDATE_NAME["name"]

# INT-053/002
def test_update_user_email_success(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "upd-email")).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=VALID_UPDATE_EMAIL)
    assert res.status_code == 200, res.text
    assert res.json()["email"] == VALID_UPDATE_EMAIL["email"]

# INT-053/003
def test_update_user_admin_toggle_success(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_ADMIN, "upd-admin")).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=VALID_UPDATE_ADMIN_TOGGLE)
    assert res.status_code == 200, res.text
    assert res.json()["admin"] == VALID_UPDATE_ADMIN_TOGGLE["admin"]

# INT-053/004
def test_update_user_invalid_role_returns_400(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "bad-role")).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json={"role": "bad_role"})
    assert res.status_code == 400, res.text
    assert "Invalid role" in res.json()["detail"]

# INT-053/005
def test_update_user_email_conflict_returns_400(client):
    first = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "dup-a")).json()
    second = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "dup-b")).json()

    res = client.patch(f"{API_BASE}/{second['user_id']}", json={"email": first["email"]})
    assert res.status_code == 400, res.text
    assert "already in use" in res.json()["detail"].lower()

# INT-053/006
def test_update_user_not_found_returns_404(client):
    res = client.patch(f"{API_BASE}/42424242", json={"name": "Ghost"})
    assert res.status_code == 404, res.text
    assert res.json()["detail"] == "User not found"

# INT-053/007
def test_update_user_not_found_after_delete_covers_101(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "cover-101")).json()
    uid = created["user_id"]

    res_del = client.delete(f"{API_BASE}/{uid}")
    assert res_del.status_code == 200 and res_del.json() is True, res_del.text

    res_patch = client.patch(f"{API_BASE}/{uid}", json={"name": "Should Not Exist"})
    assert res_patch.status_code == 404, res_patch.text
    assert res_patch.json()["detail"] == "User not found"

# INT-053/008
def test_update_large_name_ok(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "large-name")).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=LARGE_NAME)
    assert res.status_code in (200, 400), res.text

# INT-053/009
def test_update_long_email_format_validation(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "long-email")).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=LONG_EMAIL)
    assert res.status_code == 200, res.text
    assert res.json()["email"] == LONG_EMAIL["email"]

# Delete
# INT-055/001
def test_delete_user_success(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_ADMIN, "del")).json()
    uid = created["user_id"]
    res = client.delete(f"{API_BASE}/{uid}")
    assert res.status_code == 200, res.text
    assert res.json() is True

# INT-055/002
def test_delete_user_not_found_returns_404(client):
    res = client.delete(f"{API_BASE}/77777777")
    assert res.status_code == 404, res.text
    assert res.json()["detail"] == "User not found"

# Change Password

# INT-052/007
def test_change_password_success(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "pw-ok")).json()
    uid = created["user_id"]
    body = {
        "current_password": VALID_CREATE_PAYLOAD_USER["password"],
        "new_password": VALID_PASSWORD_CHANGE["new_password"],
    }
    res = client.post(f"{API_BASE}/{uid}/password", json=body)
    assert res.status_code == 200, res.text
    assert res.json() is True

# INT-052/008
def test_change_password_wrong_current_returns_403(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "pw-wrong")).json()
    uid = created["user_id"]
    res = client.post(f"{API_BASE}/{uid}/password", json=INVALID_PASSWORD_CHANGE_WRONG_CURRENT)
    assert res.status_code == 403, res.text
    assert "Current password is incorrect" in res.json()["detail"]

# INT-052/009
def test_change_password_user_not_found_returns_400(client):
    body = {"current_password": "Anything!1", "new_password": VALID_PASSWORD_CHANGE["new_password"]}
    res = client.post(f"{API_BASE}/999999/password", json=body)
    assert res.status_code == 400, res.text
    assert "User not found" in res.json()["detail"]

