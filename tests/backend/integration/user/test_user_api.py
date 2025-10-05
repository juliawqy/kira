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
        connect_args={"check_same_thread": False},  # TestClient can use threads
    )
    Base.metadata.create_all(bind=engine)

    # IMPORTANT: prevent expired/detached instances after commit
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )

    # Patch the canonical SessionLocal and the one imported by the service module
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


# -----------------------------
# Create
# -----------------------------

def test_create_user_success_admin(client):
    res = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_ADMIN, "create-admin"))
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["user_id"] > 0
    assert body["email"].startswith("alice.admin+create-admin@")
    expected_role = _payload(VALID_CREATE_PAYLOAD_ADMIN)["role"]
    assert body["role"].lower() == expected_role.lower()

def test_create_user_success_employee(client):
    res = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "create-emp"))
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["user_id"] > 0
    assert body["email"].startswith("bob.employee+create-emp@")
    expected_role = _payload(VALID_CREATE_PAYLOAD_USER)["role"]
    assert body["role"].lower() == expected_role.lower()

def test_create_user_short_password_returns_422(client):
    # Pydantic Field(min_length=8) triggers 422 before service runs
    res = client.post(f"{API_BASE}/", json=_with_unique_email(INVALID_CREATE_SHORT_PASSWORD, "short"))
    assert res.status_code == 422, res.text

def test_create_user_invalid_email_returns_422(client):
    res = client.post(f"{API_BASE}/", json=_payload(INVALID_CREATE_BAD_EMAIL))
    assert res.status_code == 422, res.text

def test_create_user_no_special_password_returns_400(client):
    # Fails service-level regex -> 400
    res = client.post(f"{API_BASE}/", json=_with_unique_email(INVALID_CREATE_NO_SPECIAL, "nospecial"))
    assert res.status_code == 400, res.text

# NEW: create -> invalid role (hits route conversion ValueError -> 400; lines 25–26)
def test_create_user_invalid_role_returns_400(client):
    bad = _with_unique_email(VALID_CREATE_PAYLOAD_USER, "badrole")
    bad["role"] = "not_a_role"
    res = client.post(f"{API_BASE}/", json=bad)
    assert res.status_code == 400, res.text
    assert "Invalid role" in res.json()["detail"]


# -----------------------------
# Read
# -----------------------------

def test_get_user_by_id_success(client):
    res = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_ADMIN, "get-by-id"))
    assert res.status_code == 201, res.text
    uid = res.json()["user_id"]

    res = client.get(f"{API_BASE}/{uid}")
    assert res.status_code == 200, res.text
    assert res.json()["user_id"] == uid

def test_get_user_by_email_success(client):
    payload = _with_unique_email(VALID_CREATE_PAYLOAD_USER, "by-email")
    assert client.post(f"{API_BASE}/", json=payload).status_code == 201
    res = client.get(f"{API_BASE}/{payload['email']}")
    assert res.status_code == 200, res.text
    assert res.json()["email"] == payload["email"]

# NEW: get_user -> numeric branch + not found (lines 57, 67–68)
def test_get_user_by_numeric_id_branch_and_404(client):
    res = client.get(f"{API_BASE}/999999")
    assert res.status_code == 404, res.text
    assert res.json()["detail"] == "User not found"


# -----------------------------
# Update (PATCH)
# -----------------------------

def test_update_user_name_success(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "upd-name")).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=VALID_UPDATE_NAME)
    assert res.status_code == 200, res.text
    assert res.json()["name"] == VALID_UPDATE_NAME["name"]

def test_update_user_email_success(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "upd-email")).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=VALID_UPDATE_EMAIL)
    assert res.status_code == 200, res.text
    assert res.json()["email"] == VALID_UPDATE_EMAIL["email"]

def test_update_user_admin_toggle_success(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_ADMIN, "upd-admin")).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=VALID_UPDATE_ADMIN_TOGGLE)
    assert res.status_code == 200, res.text
    assert res.json()["admin"] == VALID_UPDATE_ADMIN_TOGGLE["admin"]

def test_update_user_invalid_role_returns_400(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "bad-role")).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json={"role": "bad_role"})
    assert res.status_code == 400, res.text
    assert "Invalid role" in res.json()["detail"]

# NEW: update -> not found (line 101)
def test_update_user_not_found_returns_404(client):
    res = client.patch(f"{API_BASE}/42424242", json={"name": "Ghost"})
    assert res.status_code == 404, res.text
    assert res.json()["detail"] == "User not found"


# -----------------------------
# Delete
# -----------------------------

def test_delete_user_success(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_ADMIN, "del")).json()
    uid = created["user_id"]
    res = client.delete(f"{API_BASE}/{uid}")
    assert res.status_code == 200, res.text
    assert res.json() is True

# NEW: delete -> not found (line 113)
def test_delete_user_not_found_returns_404(client):
    res = client.delete(f"{API_BASE}/77777777")
    assert res.status_code == 404, res.text
    assert res.json()["detail"] == "User not found"


# -----------------------------
# Change Password
# -----------------------------

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

def test_change_password_wrong_current_returns_403(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "pw-wrong")).json()
    uid = created["user_id"]
    res = client.post(f"{API_BASE}/{uid}/password", json=INVALID_PASSWORD_CHANGE_WRONG_CURRENT)
    assert res.status_code == 403, res.text
    assert "Current password is incorrect" in res.json()["detail"]

# NEW: change_password -> user not found (line 135 else path -> 400)
def test_change_password_user_not_found_returns_400(client):
    body = {"current_password": "Anything!1", "new_password": VALID_PASSWORD_CHANGE["new_password"]}
    res = client.post(f"{API_BASE}/999999/password", json=body)
    assert res.status_code == 400, res.text
    assert "User not found" in res.json()["detail"]


# -----------------------------
# Optional edge cases
# -----------------------------

def test_update_large_name_ok(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "large-name")).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=LARGE_NAME)
    assert res.status_code in (200, 400), res.text

def test_update_long_email_format_validation(client):
    created = client.post(f"{API_BASE}/", json=_with_unique_email(VALID_CREATE_PAYLOAD_USER, "long-email")).json()
    uid = created["user_id"]
    res = client.patch(f"{API_BASE}/{uid}", json=LONG_EMAIL)
    # SQLite won't enforce length; EmailStr doesn't check length -> 200 expected
    assert res.status_code == 200, res.text
    assert res.json()["email"] == LONG_EMAIL["email"]

