"""
Test script to simulate task update and trigger email notification
Run this script to test your email notification system with the updated service interfaces
"""
import sys
import os
from datetime import date

# Add the project root to Python path so we can import modules
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(project_root)

from backend.src.services.task import update_task, add_task
from backend.src.database.db_setup import SessionLocal


def test_single_title_update():
    """Test 1: Update only the title of a task"""
    
    print("Test 1: Starting single title update test...")
    
    try:
        # First create a test task
        with SessionLocal.begin() as session:
            test_task = add_task(
                title="Original Task Title",
                description="Test task for notification",
                priority=5,
                project_id=1
            )
            task_id = test_task.id
            original_title = test_task.title
        
        print(f"📝 Created test task {task_id}: '{original_title}'")
        
        # Update only the title
        new_title = "Updated Task Title - Notification Test"
        print(f"🔄 Updating title to: '{new_title}'")
        
        updated_task = update_task(
            task_id=task_id,
            title=new_title
        )
        
        print("SUCCESS: Task title updated successfully!")
        print(f"Notification should be triggered for title change")
        print(f"   - Previous: '{original_title}'")
        print(f"   - New: '{updated_task.title}'")
            
    except Exception as e:
        print(f"ERROR: Exception occurred: {str(e)}")
        print("\n Troubleshooting tips:")
        print("1. Make sure the database is set up properly")
        print("2. Check that the notification service is configured correctly")


def test_multiple_date_updates():
    """Test 2: Update both start_date and deadline of a task"""
    
    print("\n" + "="*60)
    print("� Test 2: Starting multiple date updates test...")
    
    try:
        # First create a test task with initial dates
        with SessionLocal.begin() as session:
            test_task = add_task(
                title="Date Update Test Task",
                description="Test task for date notification",
                start_date=date(2025, 10, 1),
                deadline=date(2025, 10, 31),
                priority=3,
                project_id=1
            )
            task_id = test_task.id
            original_start = test_task.start_date
            original_deadline = test_task.deadline
        
        print(f"Created test task {task_id}: 'Date Update Test Task'")
        print(f"Original dates - Start: {original_start}, Deadline: {original_deadline}")
        
        # Update both start_date and deadline
        new_start_date = date(2025, 10, 15)
        new_deadline = date(2025, 11, 15)
        
        print(f"Updating dates to - Start: {new_start_date}, Deadline: {new_deadline}")
        
        updated_task = update_task(
            task_id=task_id,
            start_date=new_start_date,
            deadline=new_deadline
        )
        
        print("SUCCESS: Task dates updated successfully!")
        print(f"Notification should be triggered for date changes")
        print(f"   - Start date: {original_start} → {updated_task.start_date}")
        print(f"   - Deadline: {original_deadline} → {updated_task.deadline}")
            
    except Exception as e:
        print(f"ERROR: Exception occurred: {str(e)}")
        print("\n Troubleshooting tips:")
        print("1. Make sure the database is set up properly")
        print("2. Check that the notification service is configured correctly")
        print("3. Ensure the task creation was successful")


def main():
    """Main test function"""
    print("Kira Email Notification System Test")
    print("="*60)
    print("Testing the updated task notification system...")
    
    # Test 1: Single title update
    test_single_title_update()
    
    # Test 2: Multiple date updates
    test_multiple_date_updates()
    
    print("\n" + "="*60)
    print("Test completed!")
    print("\n💡 Next steps:")
    print("1. Check the console output to see if notifications were triggered")
    print("2. Check your email service configuration if you want to receive actual emails")
    print("3. The update_task function now automatically triggers notifications when fields change")


if __name__ == "__main__":
    # Run the test
    main()