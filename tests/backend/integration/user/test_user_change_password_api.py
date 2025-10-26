from __future__ import annotations

import pytest
from sqlalchemy import text
from backend.src.services.user import _verify_password

from tests.mock_data.user.integration_data import (
    VALID_USER,
    VALID_CREATE_PAYLOAD_USER,
    INVALID_USER_ID,
    VALID_PASSWORD_CHANGE,
    INVALID_PASSWORD_CHANGE_WRONG_CURRENT,
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


# INT-053/005
def test_change_password_success(client, user_base_path):

    resp = client.post(f"{user_base_path}/", json=(VALID_CREATE_PAYLOAD_USER))
    assert resp.status_code == 201

    response = client.post(f"{user_base_path}/{VALID_USER['user_id']}/password", json=VALID_PASSWORD_CHANGE)
    assert response.status_code == 200
    assert response.json() is True       

# INT-053/006
def test_change_password_wrong_current(client, user_base_path):

    resp = client.post(f"{user_base_path}/", json=(VALID_CREATE_PAYLOAD_USER))
    assert resp.status_code == 201

    response = client.post(f"{user_base_path}/{VALID_USER['user_id']}/password", json=INVALID_PASSWORD_CHANGE_WRONG_CURRENT)
    assert response.status_code == 403
    assert "Current password is incorrect" in response.json()["detail"]

# INT-053/007
def test_change_password_user_not_found(client, user_base_path):

    # other ValueError messages should map to 400 per route code

    response = client.post(f"{user_base_path}/{INVALID_USER_ID}/password", json=VALID_PASSWORD_CHANGE)
    assert response.status_code == 400
    assert "User not found" in response.json()["detail"]
        