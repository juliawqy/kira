import pytest
from unittest.mock import Mock, patch

from backend.src.services.notification import NotificationService, get_notification_service
from backend.src.schemas.email import EmailResponse, EmailRecipient
from backend.src.enums.notification import NotificationType


class TestNotificationService:

    @pytest.fixture
    def mock_email_service(self, unit_test_email):
        m = Mock()
        m._get_task_notification_recipients.return_value = [
            EmailRecipient(email=unit_test_email, name="Unit Test")
        ]
        return m

    @pytest.fixture
    def notification_service(self, mock_email_service):
        with patch('backend.src.services.notification.get_email_service', return_value=mock_email_service):
            return NotificationService()

    # UNI-124/044
    def test_init_notification_service(self, notification_service, mock_email_service):
        assert notification_service.email_service is mock_email_service

    # UNI-124/045
    def test_notify_task_updated_success(self, notification_service, mock_email_service, notification_valid_update):
        expected_response = EmailResponse(success=True, message="Email sent successfully", recipients_count=1)
        mock_email_service.send_email.return_value = expected_response

        result = notification_service.notify_task_updated(
            task_id=notification_valid_update["task_id"],
            task_title=notification_valid_update["task_title"],
            updated_fields=notification_valid_update["updated_fields"],
            previous_values=notification_valid_update.get("previous_values"),
            new_values=notification_valid_update.get("new_values"),
        )

        assert mock_email_service.send_email.call_count == 1
        assert result.success is True
        assert result.message == "Email sent successfully"
        assert result.recipients_count == 1

    # UNI-124/046
    def test_notify_task_updated_email_failure(self, notification_service, mock_email_service, notification_minimal_update):
        expected_response = EmailResponse(success=False, message="SMTP connection failed", recipients_count=0)
        mock_email_service.send_email.return_value = expected_response

        result = notification_service.notify_task_updated(
            task_id=notification_minimal_update["task_id"],
            task_title=notification_minimal_update["task_title"],
            updated_fields=notification_minimal_update["updated_fields"],
        )

        assert result.success is False
        assert result.message == "SMTP connection failed"
        assert result.recipients_count == 0

    # UNI-124/047
    def test_notify_task_updated_with_minimal_data(self, notification_service, mock_email_service, notification_minimal_update):
        expected_response = EmailResponse(success=True, message="Email sent successfully", recipients_count=1)
        mock_email_service.send_email.return_value = expected_response

        result = notification_service.notify_task_updated(
            task_id=notification_minimal_update["task_id"],
            task_title=notification_minimal_update["task_title"],
            updated_fields=notification_minimal_update["updated_fields"],
        )

        assert mock_email_service.send_email.call_count == 1
        assert result.success is True

    # UNI-124/048
    def test_notify_task_updated_exception_handling(self, notification_service, mock_email_service, notification_single_field_update):
        mock_email_service.send_email.side_effect = Exception("Unexpected error")

        result = notification_service.notify_task_updated(
            task_id=notification_single_field_update["task_id"],
            task_title=notification_single_field_update["task_title"],
            updated_fields=notification_single_field_update["updated_fields"],
        )

        assert result.success is False
        assert "Notification service error: Unexpected error" in result.message
        assert result.recipients_count == 0

    # UNI-124/049
    def test_notify_task_updated_with_all_parameters(self, notification_service, mock_email_service, notification_multiple_fields_update):
        expected_response = EmailResponse(success=True, message="Email sent successfully", recipients_count=2)
        mock_email_service.send_email.return_value = expected_response

        result = notification_service.notify_task_updated(
            task_id=notification_multiple_fields_update["task_id"],
            task_title=notification_multiple_fields_update["task_title"],
            updated_fields=notification_multiple_fields_update["updated_fields"],
            previous_values=notification_multiple_fields_update["previous_values"],
            new_values=notification_multiple_fields_update["new_values"],
        )

        assert mock_email_service.send_email.call_count == 1
        assert result.success is True
        assert result.recipients_count == 2

    # UNI-124/050
    def test_get_notification_service_singleton(self):
        s1 = get_notification_service()
        s2 = get_notification_service()
        assert s1 is s2
        assert isinstance(s1, NotificationService)

    @patch('backend.src.services.notification.logger')
    # UNI-124/051
    def test_logging_on_success(self, mock_logger, notification_service, mock_email_service, notification_minimal_update):
        mock_email_service.send_email.return_value = EmailResponse(success=True, message="Email sent successfully", recipients_count=1)

        notification_service.notify_task_updated(
            task_id=notification_minimal_update["task_id"],
            task_title=notification_minimal_update["task_title"],
            updated_fields=notification_minimal_update["updated_fields"],
        )
        mock_logger.info.assert_any_call(f"Processing task update notification for task {notification_minimal_update['task_id']}")
        mock_logger.info.assert_any_call(
            f"Activity notification '{NotificationType.TASK_UPDATE.value}' sent for task {notification_minimal_update['task_id']}"
        )

    @patch('backend.src.services.notification.logger')
    # UNI-124/052
    def test_logging_on_email_failure(self, mock_logger, notification_service, mock_email_service, notification_minimal_update):
        mock_email_service.send_email.return_value = EmailResponse(success=False, message="SMTP error", recipients_count=0)

        notification_service.notify_task_updated(
            task_id=notification_minimal_update["task_id"],
            task_title=notification_minimal_update["task_title"],
            updated_fields=notification_minimal_update["updated_fields"],
        )
        mock_logger.error.assert_called_with(
            f"Failed to send activity notification '{NotificationType.TASK_UPDATE.value}': SMTP error"
        )

    @patch('backend.src.services.notification.logger')
    # UNI-124/053
    def test_logging_on_exception(self, mock_logger, notification_service, mock_email_service, notification_minimal_update):
        mock_email_service.send_email.side_effect = Exception("Test exception")

        notification_service.notify_task_updated(
            task_id=notification_minimal_update["task_id"],
            task_title=notification_minimal_update["task_title"],
            updated_fields=notification_minimal_update["updated_fields"],
        )

        mock_logger.error.assert_called_with("Error in notify_activity: Test exception")

    @patch('backend.src.services.notification.logger')
    # UNI-124/054
    def test_notify_activity_success_logs(self, mock_logger, mock_email_service, notify_activity_success_params):
        mock_email_service.send_email.return_value = EmailResponse(success=True, message="ok", recipients_count=1)
        with patch('backend.src.services.notification.get_email_service', return_value=mock_email_service):
            svc = NotificationService()
            resp = svc.notify_activity(**notify_activity_success_params)
            assert resp.success is True
            mock_logger.info.assert_any_call(
                "Dispatching activity notification",
                extra={'type': NotificationType.TASK_UPDATE.value, 'task_id': notify_activity_success_params['task_id'], 'recipients_count': 1, 'initiated_by': notify_activity_success_params['user_email']}
            )
            mock_logger.info.assert_any_call(
                f"Activity notification '{NotificationType.TASK_UPDATE.value}' sent for task {notify_activity_success_params['task_id']}"
            )

    @patch('backend.src.services.notification.logger')
    # UNI-124/055
    def test_notify_activity_failure_logs(self, mock_logger, mock_email_service, notify_activity_failure_params):
        mock_email_service.send_email.return_value = EmailResponse(success=False, message="Boom", recipients_count=1)
        with patch('backend.src.services.notification.get_email_service', return_value=mock_email_service):
            svc = NotificationService()
            resp = svc.notify_activity(**notify_activity_failure_params)
            assert resp.success is False
            mock_logger.error.assert_called_with(
                f"Failed to send activity notification '{NotificationType.TASK_UPDATE.value}': Boom"
            )

    # UNI-124/056
    def test_notify_activity_no_recipients_returns_noop(self, mock_email_service, notify_activity_no_recipients_params):
        # Ensure fallback resolution also yields empty list
        mock_email_service._get_task_notification_recipients.return_value = []
        with patch('backend.src.services.notification.get_email_service', return_value=mock_email_service):
            svc = NotificationService()
            resp = svc.notify_activity(**notify_activity_no_recipients_params)
            assert resp.success is True
            assert resp.message == "No recipients configured for notifications"
            mock_email_service.send_email.assert_not_called()

    # UNI-124/057
    def test_notify_activity_invalid_type_returns_failure(self, mock_email_service, notify_activity_invalid_type_params):
        with patch('backend.src.services.notification.get_email_service', return_value=mock_email_service):
            svc = NotificationService()
            resp = svc.notify_activity(**notify_activity_invalid_type_params)
            assert resp.success is False
            assert "Invalid type_of_alert" in resp.message

    # UNI-124/058
    def test_notify_activity_comment_requires_user(self, mock_email_service, notify_activity_comment_missing_user_params):
        with patch('backend.src.services.notification.get_email_service', return_value=mock_email_service):
            svc = NotificationService()
            resp = svc.notify_activity(**notify_activity_comment_missing_user_params)
            assert resp.success is False
            assert "comment_user is required" in resp.message

    # UNI-124/059
    def test_notify_activity_comment_with_user_success(self, mock_email_service, notify_activity_comment_with_user_params):
        """Covers comment_ path with provided comment_user to avoid validation error."""
        mock_email_service.send_email.return_value = EmailResponse(success=True, message="ok", recipients_count=1)
        mock_email_service._get_task_notification_recipients.return_value = [EmailRecipient(email="r@example.com")]
        with patch('backend.src.services.notification.get_email_service', return_value=mock_email_service):
            svc = NotificationService()
            resp = svc.notify_activity(**notify_activity_comment_with_user_params)
            assert resp.success is True

    # UNI-124/060
    def test_notify_task_updated_exception_handler_branch(self, notification_minimal_update):
        """Force an exception within notify_task_updated try to hit its except return branch (lines 265-267)."""
        with patch('backend.src.services.notification.get_email_service') as mock_get:
            # Make constructor succeed with a mock, then patch notify_activity to raise
            mock_get.return_value = Mock(_get_task_notification_recipients=lambda self, x: [EmailRecipient(email="r@example.com")])
            svc = NotificationService()
            with patch.object(svc, 'notify_activity', side_effect=RuntimeError('boom')):
                resp = svc.notify_task_updated(
                    task_id=notification_minimal_update["task_id"],
                    task_title=notification_minimal_update["task_title"],
                    updated_fields=notification_minimal_update["updated_fields"],
                )
                assert resp.success is False
                assert "Notification service error: boom" in resp.message


class TestNotificationServiceEdgeCases:
    # UNI-124/061
    def test_notify_task_updated_empty_updated_fields(self, notification_empty_updated_fields):
        mock_email_service = Mock()
        mock_email_service.send_email.return_value = EmailResponse(success=True, message="Email sent successfully", recipients_count=1)
        mock_email_service._get_task_notification_recipients.return_value = [
            EmailRecipient(email="unit+test@example.com", name="Unit Test")
        ]

        with patch('backend.src.services.notification.get_email_service', return_value=mock_email_service):
            svc = NotificationService()
            result = svc.notify_task_updated(
                task_id=notification_empty_updated_fields["task_id"],
                task_title=notification_empty_updated_fields["task_title"],
                updated_fields=notification_empty_updated_fields["updated_fields"],
            )
            mock_email_service.send_email.assert_called_once()
            assert result.success is True

    # UNI-124/062
    def test_notify_task_updated_with_none_values(self, notification_null_values):
        mock_email_service = Mock()
        mock_email_service.send_email.return_value = EmailResponse(success=True, message="Email sent successfully", recipients_count=1)
        mock_email_service._get_task_notification_recipients.return_value = [
            EmailRecipient(email="unit+test@example.com", name="Unit Test")
        ]

        with patch('backend.src.services.notification.get_email_service', return_value=mock_email_service):
            svc = NotificationService()
            result = svc.notify_task_updated(
                task_id=notification_null_values["task_id"],
                task_title=notification_null_values["task_title"],
                updated_fields=notification_null_values["updated_fields"],
                previous_values=notification_null_values.get("previous_values"),
                new_values=notification_null_values.get("new_values"),
            )
            assert mock_email_service.send_email.call_count == 1
            assert result.success is True

    # UNI-124/063
    def test_notification_service_init_exception(self):
        with patch('backend.src.services.notification.get_email_service', side_effect=Exception("Email service error")):
            with pytest.raises(Exception):
                NotificationService()

    # UNI-124/064
    def test_notify_task_updated_large_data(self, notification_large_update):
        mock_email_service = Mock()
        mock_email_service.send_email.return_value = EmailResponse(success=True, message="Email sent successfully", recipients_count=1)
        mock_email_service._get_task_notification_recipients.return_value = [
            EmailRecipient(email="unit+test@example.com", name="Unit Test")
        ]

        with patch('backend.src.services.notification.get_email_service', return_value=mock_email_service):
            svc = NotificationService()
            result = svc.notify_task_updated(
                task_id=notification_large_update["task_id"],
                task_title=notification_large_update["task_title"],
                updated_fields=notification_large_update["updated_fields"],
                previous_values=notification_large_update["previous_values"],
                new_values=notification_large_update["new_values"],
            )
            mock_email_service.send_email.assert_called_once()
            assert result.success is True

    # UNI-124/065
    def test_get_notification_service_direct(self):
        svc = get_notification_service()
        assert isinstance(svc, NotificationService)

    # UNI-124/066
    @patch('backend.src.services.notification.get_email_service')
    def test_build_activity_message_with_invalid_type_falls_back_to_raw_type(self, mock_get_email_service, custom_event_activity_params):
        mock_get_email_service.return_value = Mock()
        svc = NotificationService()
        subject, text_body, html_body = svc._build_activity_message(
            type_of_alert=custom_event_activity_params["type_of_alert"],
            task_id=custom_event_activity_params["task_id"],
            task_title=custom_event_activity_params["task_title"],
            user_email=custom_event_activity_params["user_email"],
            comment_user=None,
            updated_fields=custom_event_activity_params["updated_fields"],
            old_values=custom_event_activity_params["old_values"],
            new_values=custom_event_activity_params["new_values"],
        )
        
        assert "Custom_Event" in subject
        assert "Custom_Event" in text_body
        assert "Custom_Event" in html_body