from __future__ import annotations

import pytest
from sqlalchemy import text
from backend.src.services.user import _verify_password

from tests.mock_data.user.integration_data import (
    VALID_USER_ADMIN,
    VALID_USER,
    VALID_CREATE_PAYLOAD_USER,
    INVALID_USER_ID,
)

@pytest.fixture
def test_db_session(test_engine):
    """
    Create a database session using the same SessionLocal as the API.
    """
    from sqlalchemy.orm import sessionmaker
    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )

    with TestingSessionLocal() as session:
        yield session

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


# INT-054/001
def test_get_user_by_id_success(client, user_base_path):

    resp = client.post(f"{user_base_path}/", json=(VALID_CREATE_PAYLOAD_USER))
    assert resp.status_code == 201

    response = client.get(f"{user_base_path}/{VALID_USER['user_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == VALID_USER["email"]      

# INT-054/002
def test_get_user_by_non_digit_identifier_success(client, user_base_path):
    # exercise the non-digit branch (identifier.isdigit() == False)

    identifier = VALID_USER["email"]
    resp = client.post(f"{user_base_path}/", json=(VALID_CREATE_PAYLOAD_USER))
    assert resp.status_code == 201

    response = client.get(f"{user_base_path}/{identifier}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == VALID_USER["email"]        

# INT-054/003
def test_get_user_not_found(client, user_base_path):

    response = client.get(f"{user_base_path}/{INVALID_USER_ID}")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# INT-054/004
def test_list_users_success(client, user_base_path):
    
    for payload in (VALID_USER_ADMIN, VALID_USER):
        resp = client.post(f"{user_base_path}/", json=(payload))
        assert resp.status_code == 201

    response = client.get(f"{user_base_path}/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    assert len(data) == 2
    emails = {u["email"] for u in data}
    assert VALID_USER["email"] in emails and VALID_USER_ADMIN["email"] in emails