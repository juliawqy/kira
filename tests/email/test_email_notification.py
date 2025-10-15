"""
Test script to simulate task update and trigger email notification
This aligns with services/task.update_task auto-notification and current email_service behavior.
"""
import sys
import os
from datetime import date

# Add the project root to Python path so we can import modules when running directly
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(project_root)

from backend.src.services.task import update_task, add_task


def test_priority_update():
    """Simulate updating the task priority to trigger a notification."""
    print("Kira Email Notification: Priority Update Test")
    print("=" * 60)

    try:
        # 1) Create a test task with an initial priority
        test_task = add_task(
            title="Priority Update Test Task",
            description="Testing notification on priority change",
            priority=3,
            project_id=1,
        )
        task_id = test_task.id
        original_priority = test_task.priority
        print(f"📝 Created test task {task_id} with priority {original_priority}")

        # 2) Update only the priority (this should trigger update_task's notification flow)
        new_priority = 7
        print(f"🔄 Updating priority to: {new_priority}")

        updated_task = update_task(
            task_id=task_id,
            priority=new_priority,
        )

        print("SUCCESS: Task priority updated!")
        print("Notification should be triggered for priority change.")
        print(f"   - Previous priority: {original_priority}")
        print(f"   - New priority:      {updated_task.priority}")

        print("\nNote: By default, EmailService uses a stub for recipients.\n"
              "If no recipients are configured, it logs and returns a success message without sending.\n"
              "To test actual sending, configure FASTMAIL_* env vars and implement\n"
              "EmailService._get_task_notification_recipients().")

    except Exception as e:
        print(f"ERROR: Exception occurred: {str(e)}")
        print("\nTroubleshooting:")
        print("- Ensure the SQLite DB exists (see README for setup command)")
        print("- Verify backend.src.database paths and that add_task works")
        print("- Check email settings and recipient configuration if expecting real emails")


if __name__ == "__main__":
    # Run the test directly
    test_priority_update()
