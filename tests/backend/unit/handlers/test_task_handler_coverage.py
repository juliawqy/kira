import pytest
from unittest.mock import Mock, patch
from backend.src.handlers.task_handler import add_comment, update_comment, delete_comment


class TestTaskHandlerCoverage:
    """Test cases to cover uncovered lines in task_handler.py"""
    
    @patch('backend.src.handlers.task_handler.task_service')
    @patch('backend.src.handlers.task_handler.user_service')
    @patch('backend.src.handlers.task_handler.comment_service')
    @patch('backend.src.handlers.task_handler.logger')
    def test_add_comment_with_recipient_emails(self, mock_logger, mock_comment_service, mock_user_service, mock_task_service):
        """Test add_comment with recipient_emails to cover lines 52-55"""
        # Setup mocks
        mock_task_service.get_task_with_subtasks.return_value = {"id": 1}
        mock_user_service.get_user.return_value = {"id": 1, "email": "test@example.com"}
        mock_comment_service.add_comment.return_value = {"comment_id": 1, "comment": "test"}
        
        # Test with recipient emails
        recipient_emails = ["nonexistent@example.com", "valid@example.com"]
        
        # Mock user_service.get_user to return None for first email, valid user for second
        def mock_get_user(email):
            if email == "nonexistent@example.com":
                return None
            return {"id": 2, "email": email}
        
        mock_user_service.get_user.side_effect = mock_get_user
        
        result = add_comment(1, 1, "test comment", recipient_emails)
        
        # Verify the warning was logged for nonexistent email
        mock_logger.warning.assert_called_once_with("Recipient email nonexistent@example.com not found in system")
        assert result == {"comment_id": 1, "comment": "test"}
    
    @patch('backend.src.handlers.task_handler.comment_service')
    def test_update_comment_value_error_handling(self, mock_comment_service):
        """Test update_comment ValueError handling to cover lines 89-90"""
        # Setup mock to raise ValueError
        mock_comment_service.get_comment.return_value = {"comment_id": 1, "user_id": 1}
        mock_comment_service.update_comment.side_effect = ValueError("Comment not found")
        
        # Test that ValueError is re-raised
        with pytest.raises(ValueError, match="Comment not found"):
            update_comment(1, "updated text", 1)
    
    @patch('backend.src.handlers.task_handler.comment_service')
    def test_delete_comment_value_error_handling(self, mock_comment_service):
        """Test delete_comment ValueError handling to cover lines 106-107"""
        # Setup mock to raise ValueError
        mock_comment_service.get_comment.return_value = {"comment_id": 1, "user_id": 1}
        mock_comment_service.delete_comment.side_effect = ValueError("Comment not found")
        
        # Test that ValueError is re-raised
        with pytest.raises(ValueError, match="Comment not found"):
            delete_comment(1, 1)
