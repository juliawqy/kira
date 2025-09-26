# from unittest.mock import patch, MagicMock
# from fastapi.testclient import TestClient
# from tests.mock_data.user_data import VALID_USER_1

# # KIRA-002/102 - get user endpoint
# @patch("backend.src.api.user.get_user")
# def test_get_user_endpoint(mock_get_user):
#     from backend.src.api import user as user_api
#     client = TestClient(user_api.router)

#     mock_get_user.return_value = VALID_USER_1
#     resp = client.get("/users/1")
#     assert resp.status_code == 200
#     assert resp.json()["email"] == VALID_USER_1["email"]
