# import pytest
# from fastapi.testclient import TestClient
# from backend.src.main import app  # adjust if your FastAPI entrypoint differs

# client = TestClient(app)

# # KIRA-API-002/005 - list users API success
# def test_list_users_api_success():
#     # Arrange: create some users first
#     client.post("/users", json={"email": "alice@example.com", "full_name": "Alice"})
#     client.post("/users", json={"email": "bob@example.com", "full_name": "Bob"})

#     # Act
#     response = client.get("/users")

#     # Assert
#     assert response.status_code == 200
#     users = response.json()
#     assert isinstance(users, list)
#     assert any(u["email"] == "alice@example.com" for u in users)
#     assert any(u["email"] == "bob@example.com" for u in users)
