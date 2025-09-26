# from unittest.mock import patch, MagicMock
# from fastapi.testclient import TestClient
# from tests.mock_data.user_data import VALID_CREATE, VALID_USER_1

# # KIRA-002/101 - create user endpoint
# @patch("backend.src.api.user.create_user")
# def test_create_user_endpoint(mock_create_user):
#     from backend.src.api import user as user_api  # adjust as needed
#     client = TestClient(user_api.router)  # or import your FastAPI `app` if routes are mounted on app

#     mock_create_user.return_value = VALID_USER_1

#     resp = client.post("/users", json=VALID_CREATE)
#     assert resp.status_code == 201
#     assert resp.json()["id"] == VALID_USER_1["id"]
