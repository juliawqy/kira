from __future__ import annotations

import pytest
from sqlalchemy import text
from backend.src.services.user import _verify_password

from tests.mock_data.user.integration_data import (
    VALID_USER,
    VALID_CREATE_PAYLOAD_ADMIN,
    VALID_CREATE_PAYLOAD_USER,
    INVALID_USER_ID,
    VALID_UPDATE_NAME,
    INVALID_EMAIL_UPDATE,
    INVALID_INVALID_ROLE_UPDATE,
)

@pytest.fixture
def verify_database_state(test_db_session):
    """
    Fixture to verify database state before and after tests.
    """
    def _verify_state():
        result = test_db_session.execute(text("SELECT COUNT(*) FROM user"))
        return result.scalar()

    initial_count = _verify_state()
    yield _verify_state
    final_count = _verify_state()

    if final_count != initial_count:
        print(f"Database state changed: {initial_count} -> {final_count} users")
   

# INT-053/001
def test_update_user_name_success(client, user_base_path):

    resp = client.post(f"{user_base_path}/", json=(VALID_CREATE_PAYLOAD_USER))
    assert resp.status_code == 201

    response = client.patch(f"{user_base_path}/{VALID_USER['user_id']}", json=VALID_UPDATE_NAME)
    assert response.status_code == 200
    assert response.json()["name"] == VALID_UPDATE_NAME["name"]

# INT-053/002
def test_update_user_not_found(client, user_base_path):
    response = client.patch(f"{user_base_path}/{INVALID_USER_ID}", json=VALID_UPDATE_NAME)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# INT-053/003
def test_update_user_email_already_exists(client, user_base_path):
    # exercise ValueError path in update_user

    resp = client.post(f"{user_base_path}/", json=(VALID_CREATE_PAYLOAD_USER))
    assert resp.status_code == 201

    resp = client.post(f"{user_base_path}/", json=(VALID_CREATE_PAYLOAD_ADMIN))
    assert resp.status_code == 201

    response = client.patch(f"{user_base_path}/{VALID_USER['user_id']}", json=INVALID_EMAIL_UPDATE)
    assert response.status_code == 400
    assert "Email already in use" in response.json()["detail"]
    
# INT-053/004
def test_update_user_invalid_role(client, user_base_path):
    # exercise ValueError path in update_user for invalid role

    resp = client.post(f"{user_base_path}/", json=(VALID_CREATE_PAYLOAD_USER))
    assert resp.status_code == 201

    response = client.patch(f"{user_base_path}/{VALID_USER['user_id']}", json=INVALID_INVALID_ROLE_UPDATE)
    assert response.status_code == 400
