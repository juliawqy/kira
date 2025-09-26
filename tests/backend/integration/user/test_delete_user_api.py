# from unittest.mock import patch
# from fastapi.testclient import TestClient

# # KIRA-002/104 - delete user endpoint
# @patch("backend.src.api.user.delete_user")
# def test_delete_user_endpoint(mock_delete_user):
#     from backend.src.api import user as user_api
#     client = TestClient(user_api.router)

#     mock_delete_user.return_value = None
#     resp = client.delete("/users/999")
#     assert resp.status_code == 204
