"""
Unit tests for NotificationService
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import logging

from backend.src.services.notification_service import NotificationService, get_notification_service
from backend.src.schemas.email import EmailResponse


class TestNotificationService:
    """Test cases for NotificationService class"""

    @pytest.fixture
    def mock_email_service(self):
        """Mock email service for testing"""
        mock_service = Mock()
        return mock_service

    @pytest.fixture
    def notification_service(self, mock_email_service):
        """Create NotificationService instance with mocked email service"""
        with patch('backend.src.services.notification_service.get_email_service', return_value=mock_email_service):
            return NotificationService()

    def test_init_notification_service(self, notification_service, mock_email_service):
        """Test NotificationService initialization"""
        assert notification_service.email_service is mock_email_service

    def test_notify_task_updated_success(self, notification_service, mock_email_service):
        """Test successful task update notification"""
        # Setup mock email service response
        expected_response = EmailResponse(
            success=True,
            message="Email sent successfully",
            recipients_count=1
        )
        mock_email_service.send_task_update_notification.return_value = expected_response

        # Test data
        task_id = 123
        task_title = "Test Task"
        updated_fields = ["title", "priority"]
        previous_values = {"title": "Old Title", "priority": 3}
        new_values = {"title": "New Title", "priority": 5}
        task_url = "http://localhost:8000/tasks/123"

        # Call the method
        result = notification_service.notify_task_updated(
            task_id=task_id,
            task_title=task_title,
            updated_fields=updated_fields,
            previous_values=previous_values,
            new_values=new_values,
            task_url=task_url
        )

        # Verify email service was called correctly
        mock_email_service.send_task_update_notification.assert_called_once_with(
            task_id=task_id,
            task_title=task_title,
            updated_fields=updated_fields,
            previous_values=previous_values,
            new_values=new_values,
            task_url=task_url
        )

        # Verify response
        assert result.success is True
        assert result.message == "Email sent successfully"
        assert result.recipients_count == 1

    def test_notify_task_updated_email_failure(self, notification_service, mock_email_service):
        """Test task update notification when email service fails"""
        # Setup mock email service to return failure response
        expected_response = EmailResponse(
            success=False,
            message="SMTP connection failed",
            recipients_count=0
        )
        mock_email_service.send_task_update_notification.return_value = expected_response

        result = notification_service.notify_task_updated(
            task_id=123,
            task_title="Test Task",
            updated_fields=["title"]
        )

        # Verify response indicates failure
        assert result.success is False
        assert result.message == "SMTP connection failed"
        assert result.recipients_count == 0

    def test_notify_task_updated_with_minimal_data(self, notification_service, mock_email_service):
        """Test task update notification with minimal required data"""
        expected_response = EmailResponse(
            success=True,
            message="Email sent successfully",
            recipients_count=1
        )
        mock_email_service.send_task_update_notification.return_value = expected_response

        result = notification_service.notify_task_updated(
            task_id=456,
            task_title="Minimal Task",
            updated_fields=["description"]
        )

        # Verify email service was called with correct parameters
        mock_email_service.send_task_update_notification.assert_called_once_with(
            task_id=456,
            task_title="Minimal Task",
            updated_fields=["description"],
            previous_values=None,
            new_values=None,
            task_url=None
        )

        assert result.success is True

    def test_notify_task_updated_exception_handling(self, notification_service, mock_email_service):
        """Test exception handling in notify_task_updated"""
        # Setup mock to raise exception
        mock_email_service.send_task_update_notification.side_effect = Exception("Unexpected error")

        result = notification_service.notify_task_updated(
            task_id=789,
            task_title="Error Task",
            updated_fields=["status"]
        )

        # Verify error response
        assert result.success is False
        assert "Notification service error: Unexpected error" in result.message
        assert result.recipients_count == 0

    def test_notify_task_updated_with_all_parameters(self, notification_service, mock_email_service):
        """Test task update notification with all optional parameters"""
        expected_response = EmailResponse(
            success=True,
            message="Email sent successfully",
            recipients_count=2
        )
        mock_email_service.send_task_update_notification.return_value = expected_response

        # Complete test data
        task_id = 999
        task_title = "Complete Task Test"
        updated_fields = ["title", "description", "priority", "deadline"]
        previous_values = {
            "title": "Old Title",
            "description": "Old Description",
            "priority": 3,
            "deadline": "2025-10-01"
        }
        new_values = {
            "title": "New Title", 
            "description": "New Description",
            "priority": 5,
            "deadline": "2025-10-15"
        }
        task_url = "http://localhost:8000/tasks/999"

        result = notification_service.notify_task_updated(
            task_id=task_id,
            task_title=task_title,
            updated_fields=updated_fields,
            previous_values=previous_values,
            new_values=new_values,
            task_url=task_url
        )

        # Verify all parameters were passed correctly
        mock_email_service.send_task_update_notification.assert_called_once_with(
            task_id=task_id,
            task_title=task_title,
            updated_fields=updated_fields,
            previous_values=previous_values,
            new_values=new_values,
            task_url=task_url
        )

        assert result.success is True
        assert result.recipients_count == 2

    def test_get_notification_service_singleton(self):
        """Test that get_notification_service returns the same instance"""
        service1 = get_notification_service()
        service2 = get_notification_service()
        
        assert service1 is service2
        assert isinstance(service1, NotificationService)

    @patch('backend.src.services.notification_service.logger')
    def test_logging_on_success(self, mock_logger, notification_service, mock_email_service):
        """Test that appropriate logs are generated on successful notification"""
        expected_response = EmailResponse(
            success=True,
            message="Email sent successfully",
            recipients_count=1
        )
        mock_email_service.send_task_update_notification.return_value = expected_response

        notification_service.notify_task_updated(
            task_id=123,
            task_title="Test Task",
            updated_fields=["title"]
        )

        # Verify logging calls
        mock_logger.info.assert_any_call("Processing task update notification for task 123")
        mock_logger.info.assert_any_call("Task update notification sent successfully for task 123")

    @patch('backend.src.services.notification_service.logger')
    def test_logging_on_email_failure(self, mock_logger, notification_service, mock_email_service):
        """Test that appropriate logs are generated on email service failure"""
        expected_response = EmailResponse(
            success=False,
            message="SMTP error",
            recipients_count=0
        )
        mock_email_service.send_task_update_notification.return_value = expected_response

        notification_service.notify_task_updated(
            task_id=123,
            task_title="Test Task",
            updated_fields=["title"]
        )

        # Verify error logging
        mock_logger.error.assert_called_with("Failed to send task update notification: SMTP error")

    @patch('backend.src.services.notification_service.logger')
    def test_logging_on_exception(self, mock_logger, notification_service, mock_email_service):
        """Test that appropriate logs are generated on exception"""
        mock_email_service.send_task_update_notification.side_effect = Exception("Test exception")

        notification_service.notify_task_updated(
            task_id=123,
            task_title="Test Task",
            updated_fields=["title"]
        )

        # Verify exception logging
        mock_logger.error.assert_called_with("Error in notify_task_updated: Test exception")


class TestNotificationServiceEdgeCases:
    """Test edge cases and error conditions for NotificationService"""

    def test_notify_task_updated_empty_updated_fields(self):
        """Test notification with empty updated_fields list"""
        mock_email_service = Mock()
        expected_response = EmailResponse(
            success=True,
            message="Email sent successfully",
            recipients_count=1
        )
        mock_email_service.send_task_update_notification.return_value = expected_response

        with patch('backend.src.services.notification_service.get_email_service', return_value=mock_email_service):
            notification_service = NotificationService()
            
            result = notification_service.notify_task_updated(
                task_id=123,
                task_title="Test Task",
                updated_fields=[]  # Empty list
            )

            # Should still call email service
            mock_email_service.send_task_update_notification.assert_called_once()
            assert result.success is True

    def test_notify_task_updated_with_none_values(self):
        """Test notification with None values for optional parameters"""
        mock_email_service = Mock()
        expected_response = EmailResponse(
            success=True,
            message="Email sent successfully",
            recipients_count=1
        )
        mock_email_service.send_task_update_notification.return_value = expected_response

        with patch('backend.src.services.notification_service.get_email_service', return_value=mock_email_service):
            notification_service = NotificationService()
            
            result = notification_service.notify_task_updated(
                task_id=123,
                task_title="Test Task",
                updated_fields=["title"],
                previous_values=None,
                new_values=None,
                task_url=None
            )

            # Verify None values are passed correctly
            mock_email_service.send_task_update_notification.assert_called_once_with(
                task_id=123,
                task_title="Test Task",
                updated_fields=["title"],
                previous_values=None,
                new_values=None,
                task_url=None
            )
            assert result.success is True

    def test_notification_service_init_exception(self):
        """Test NotificationService initialization when email service fails"""
        with patch('backend.src.services.notification_service.get_email_service', side_effect=Exception("Email service error")):
            with pytest.raises(Exception):
                NotificationService()

    def test_notify_task_updated_large_data(self):
        """Test notification with large data sets"""
        mock_email_service = Mock()
        expected_response = EmailResponse(
            success=True,
            message="Email sent successfully",
            recipients_count=1
        )
        mock_email_service.send_task_update_notification.return_value = expected_response

        with patch('backend.src.services.notification_service.get_email_service', return_value=mock_email_service):
            notification_service = NotificationService()
            
            # Large updated_fields list
            large_updated_fields = [f"field_{i}" for i in range(100)]
            
            # Large data dictionaries
            large_previous_values = {f"field_{i}": f"old_value_{i}" for i in range(100)}
            large_new_values = {f"field_{i}": f"new_value_{i}" for i in range(100)}
            
            result = notification_service.notify_task_updated(
                task_id=123,
                task_title="Large Data Task",
                updated_fields=large_updated_fields,
                previous_values=large_previous_values,
                new_values=large_new_values
            )

            # Should handle large data without issues
            mock_email_service.send_task_update_notification.assert_called_once()
            assert result.success is True