from __future__ import annotations

import pytest
from sqlalchemy import text
from backend.src.services.user import _verify_password

from tests.mock_data.user.integration_data import (
    VALID_USER,
    VALID_CREATE_PAYLOAD_USER,
    INVALID_USER_ID,
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

# INT-055/001
def test_delete_user_success(client, user_base_path):
    resp = client.post(f"{user_base_path}/", json=(VALID_CREATE_PAYLOAD_USER))
    assert resp.status_code == 201

    response = client.delete(f"{user_base_path}/{VALID_USER['user_id']}")
    assert response.status_code == 200

# INT-055/002
def test_delete_user_not_found(client, user_base_path):
    response = client.delete(f"{user_base_path}/{INVALID_USER_ID}")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
