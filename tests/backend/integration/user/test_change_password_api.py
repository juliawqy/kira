# from unittest.mock import patch
# from fastapi.testclient import TestClient

# # KIRA-002/105 - change password endpoint
# @patch("backend.src.api.user.change_password")
# def test_change_password_endpoint(mock_change_password):
#     from backend.src.api import user as user_api
#     client = TestClient(user_api.router)

#     mock_change_password.return_value = True
#     resp = client.post("/users/42/change-password", json={"old_password": "old", "new_password": "new"})
#     assert resp.status_code == 200
