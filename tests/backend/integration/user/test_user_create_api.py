from __future__ import annotations

import pytest
from sqlalchemy import text
from backend.src.services.user import _verify_password

from tests.mock_data.user.integration_data import (
    VALID_USER_ADMIN,
    VALID_USER,
    VALID_CREATE_PAYLOAD_ADMIN,
    VALID_CREATE_PAYLOAD_USER,
    INVALID_CREATE_SHORT_PASSWORD,
    INVALID_CREATE_NO_SPECIAL,
    INVALID_CREATE_BAD_EMAIL,
    INVALID_CREATE_BAD_ROLE,
    INVALID_CREATE_NO_NAME,
    INVALID_CREATE_BAD_ADMIN,
    INVALID_CREATE_UNAUTHORISED,
    INVALID_CREATE_INVALID_DEPARTMENT
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


# INT-052/001
def test_create_user_success_admin(client, user_base_path, test_db_session, verify_database_state):

    initial_count = verify_database_state()

    response = client.post(f"{user_base_path}/", json=VALID_CREATE_PAYLOAD_ADMIN)
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == VALID_USER_ADMIN["user_id"]
    assert data["admin"] is True

    expected_response = VALID_USER_ADMIN
    for field, expected_value in expected_response.items():
        if field in data:
            assert data[field] == expected_value, f"Field {field}: expected {expected_value}, got {data[field]}"
    
    db_result = test_db_session.execute(
        text("SELECT name, email, role, department_id, admin, hashed_pw FROM user WHERE user_id = :user_id"),
        {"user_id": expected_response["user_id"]}
    ).fetchone()
    assert db_result is not None
    assert db_result[0] == expected_response["name"]
    assert db_result[1] == expected_response["email"]
    assert db_result[2] == expected_response["role"]
    assert db_result[3] == expected_response["department_id"]
    assert db_result[4] == expected_response["admin"]
    assert _verify_password(expected_response["password"], db_result[5]) is True

    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-052/002
def test_create_user_success_employee(client, user_base_path, test_db_session, verify_database_state):

    initial_count = verify_database_state()

    response = client.post(f"{user_base_path}/", json=VALID_CREATE_PAYLOAD_USER)
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == VALID_USER["user_id"]
    assert data["admin"] is False

    expected_response = VALID_USER
    for field, expected_value in expected_response.items():
        if field in data:
            assert data[field] == expected_value, f"Field {field}: expected {expected_value}, got {data[field]}"
    
    db_result = test_db_session.execute(
        text("SELECT name, email, role, department_id, admin, hashed_pw FROM user WHERE user_id = :user_id"),
        {"user_id": expected_response["user_id"]}
    ).fetchone()
    assert db_result is not None
    assert db_result[0] == expected_response["name"]
    assert db_result[1] == expected_response["email"]
    assert db_result[2] == expected_response["role"]
    assert db_result[3] == expected_response["department_id"]
    assert db_result[4] == expected_response["admin"]
    assert _verify_password(expected_response["password"], db_result[5]) is True

    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-052/003
def test_create_user_failure_duplicate_email(client, user_base_path, test_db_session, verify_database_state):
    initial_count = verify_database_state()

    response = client.post(f"{user_base_path}/", json=VALID_CREATE_PAYLOAD_ADMIN)
    assert response.status_code == 201

    response = client.post(f"{user_base_path}/", json=VALID_CREATE_PAYLOAD_ADMIN)
    assert response.status_code == 400
    assert "User with this email already exists" in response.json()["detail"]

    final_count = verify_database_state()
    assert final_count == initial_count + 1

# INT-052/004
@pytest.mark.parametrize(
    "invalid_payload, expected_status",
    [
        (INVALID_CREATE_SHORT_PASSWORD, 422),   
        (INVALID_CREATE_NO_SPECIAL, 400),       
        (INVALID_CREATE_BAD_EMAIL, 422),        
        (INVALID_CREATE_BAD_ROLE, 400),        
        (INVALID_CREATE_NO_NAME, 422),          
        (INVALID_CREATE_BAD_ADMIN, 422),        
        (INVALID_CREATE_UNAUTHORISED, 403),     
        (INVALID_CREATE_INVALID_DEPARTMENT, 400),
    ],
)
def test_create_user_invalid_payload(client, user_base_path, invalid_payload, expected_status):
    response = client.post(f"{user_base_path}/", json=invalid_payload)
    assert response.status_code == expected_status, (
        f"Payload {invalid_payload} expected {expected_status}, got {response.status_code}, body={response.json()}"
    )