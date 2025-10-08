import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.src.main import app
from tests.mock_data.user.unit_data import (
    VALID_USER_ADMIN,
    VALID_USER,
    VALID_CREATE_PAYLOAD_ADMIN,
    VALID_CREATE_PAYLOAD_USER,
    INVALID_USER_ID,
    VALID_UPDATE_NAME,
    VALID_PASSWORD_CHANGE,
)

client = TestClient(app)

BASE = "/kira/app/api/v1/user"  # full router prefix


# -----------------------------
# Create User
# -----------------------------
def test_create_user_success_admin():
    with patch("backend.src.api.v1.routes.user_route.user_service.create_user", return_value=VALID_USER_ADMIN):
        response = client.post(f"{BASE}/", json=VALID_CREATE_PAYLOAD_ADMIN)
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == VALID_USER_ADMIN["user_id"]
        assert data["admin"] is True


def test_create_user_success_employee():
    with patch("backend.src.api.v1.routes.user_route.user_service.create_user", return_value=VALID_USER):
        response = client.post(f"{BASE}/", json=VALID_CREATE_PAYLOAD_USER)
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == VALID_USER["user_id"]
        assert data["admin"] is False


def test_create_user_failure_duplicate_email():
    with patch(
        "backend.src.api.v1.routes.user_route.user_service.create_user",
        side_effect=ValueError("Email already exists")
    ):
        response = client.post(f"{BASE}/", json=VALID_CREATE_PAYLOAD_USER)
        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]


def test_create_user_invalid_payload_returns_422():
    # missing required field `email` should cause pydantic validation error -> 422
    invalid_payload = {
        "name": "No Email",
        # "email": missing
        "role": "employee",
        "password": "Some!Pass123",
        "department_id": None,
        "admin": False,
    }
    response = client.post(f"{BASE}/", json=invalid_payload)
    assert response.status_code == 422
    # minimal assertion that validation error refers to `email` or required fields
    body = response.json()
    assert "detail" in body
    # ensure at least one error item (structure depends on FastAPI/pydantic)
    assert isinstance(body["detail"], list) and len(body["detail"]) > 0


# -----------------------------
# Get User
# -----------------------------
def test_get_user_by_id_success():
    with patch("backend.src.api.v1.routes.user_route.user_service.get_user", return_value=VALID_USER):
        response = client.get(f"{BASE}/{VALID_USER['user_id']}")
        assert response.status_code == 200
        assert response.json()["email"] == VALID_USER["email"]


def test_get_user_by_non_digit_identifier_success():
    # exercise the non-digit branch (identifier.isdigit() == False)
    identifier = VALID_USER["email"]
    with patch("backend.src.api.v1.routes.user_route.user_service.get_user", return_value=VALID_USER) as mock_get:
        response = client.get(f"{BASE}/{identifier}")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == VALID_USER["email"]
        # ensure service was called with the string identifier (not int)
        mock_get.assert_called_with(identifier)


def test_get_user_not_found():
    with patch("backend.src.api.v1.routes.user_route.user_service.get_user", return_value=None):
        response = client.get(f"{BASE}/{INVALID_USER_ID}")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"


def test_list_users_success():
    users = [VALID_USER, VALID_USER_ADMIN]
    with patch("backend.src.api.v1.routes.user_route.user_service.list_users", return_value=users):
        response = client.get(f"{BASE}/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        emails = {u["email"] for u in data}
        assert VALID_USER["email"] in emails and VALID_USER_ADMIN["email"] in emails


# -----------------------------
# Update User
# -----------------------------
def test_update_user_name_success():
    updated_user = VALID_USER.copy()
    updated_user.update(VALID_UPDATE_NAME)
    with patch("backend.src.api.v1.routes.user_route.user_service.update_user", return_value=updated_user):
        response = client.patch(f"{BASE}/{VALID_USER['user_id']}", json=VALID_UPDATE_NAME)
        assert response.status_code == 200
        assert response.json()["name"] == VALID_UPDATE_NAME["name"]


def test_update_user_not_found():
    with patch("backend.src.api.v1.routes.user_route.user_service.update_user", return_value=None):
        response = client.patch(f"{BASE}/{INVALID_USER_ID}", json=VALID_UPDATE_NAME)
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"


def test_update_user_email_already_exists():
    # exercise ValueError path in update_user
    with patch(
        "backend.src.api.v1.routes.user_route.user_service.update_user",
        side_effect=ValueError("Email already exists")
    ):
        response = client.patch(f"{BASE}/{VALID_USER['user_id']}", json={"email": "someone@else.com"})
        assert response.status_code == 400
        assert "Email already exists" in response.json()["detail"]


# -----------------------------
# Delete User
# -----------------------------
def test_delete_user_success():
    with patch("backend.src.api.v1.routes.user_route.user_service.delete_user", return_value=True):
        response = client.delete(f"{BASE}/{VALID_USER['user_id']}")
        assert response.status_code == 200
        assert response.json() is True


def test_delete_user_not_found():
    with patch("backend.src.api.v1.routes.user_route.user_service.delete_user", return_value=False):
        response = client.delete(f"{BASE}/{INVALID_USER_ID}")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"


# -----------------------------
# Change Password
# -----------------------------
def test_change_password_success():
    with patch("backend.src.api.v1.routes.user_route.user_service.change_password", return_value=True):
        response = client.post(f"{BASE}/{VALID_USER_ADMIN['user_id']}/password", json=VALID_PASSWORD_CHANGE)
        assert response.status_code == 200
        assert response.json() is True


def test_change_password_wrong_current():
    with patch(
        "backend.src.api.v1.routes.user_route.user_service.change_password",
        side_effect=ValueError("Current password is incorrect")
    ):
        response = client.post(f"{BASE}/{VALID_USER_ADMIN['user_id']}/password", json=VALID_PASSWORD_CHANGE)
        assert response.status_code == 403
        assert "Current password is incorrect" in response.json()["detail"]


def test_change_password_user_not_found():
    # other ValueError messages should map to 400 per route code
    with patch(
        "backend.src.api.v1.routes.user_route.user_service.change_password",
        side_effect=ValueError("User not found")
    ):
        response = client.post(f"{BASE}/{VALID_USER_ADMIN['user_id']}/password", json=VALID_PASSWORD_CHANGE)
        assert response.status_code == 400
        assert "User not found" in response.json()["detail"]
