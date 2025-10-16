# import pytest
# from unittest.mock import MagicMock, patch


# @pytest.fixture(autouse=True)
# def patch_sessionlocal():
#     """
#     Automatically patch backend.src.services.user.SessionLocal for all tests
#     in this module. Provides a mock session object that can be configured
#     inside each test.
#     """
#     with patch("backend.src.services.user.SessionLocal") as mock_session_local:
#         mock_session = MagicMock()

#         mock_session_local.begin.return_value.__enter__.return_value = mock_session
#         yield mock_session
