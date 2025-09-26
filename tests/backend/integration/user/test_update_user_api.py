# from unittest.mock import patch
# from fastapi.testclient import TestClient

# # KIRA-002/103 - patch user endpoint
# @patch("backend.src.api.user.update_user")
# def test_update_user_endpoint(mock_update_user):
#     from backend.src.api import user as user_api
#     client = TestClient(user_api.router)

#     mock_update_user.return_value = {"id": 5, "full_name": "Updated Name"}
#     resp = client.patch("/users/5", json={"full_name": "Updated Name"})
#     assert resp.status_code == 200
#     assert resp.json()["full_name"] == "Updated Name"
