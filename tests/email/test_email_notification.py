"""
Test script to simulate task update and trigger email notification
Run this script to test your email notification system
"""
import sys
import os

# Add the project root to Python path so we can import modules
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(project_root)

from backend.src.services.notification_service import get_notification_service


def test_task_update_notification():
    """Test sending a task update notification email"""
    
    print("🚀 Starting email notification test...")
    
    # Get the notification service
    notification_service = get_notification_service()
    
    # Simulate task update data
    test_data = {
        "task_id": 123,
        "task_title": "Complete Project Documentation",
        "updated_by": "Kira Hoora",
        "updated_fields": ["Status", "Priority", "Deadline"],
        "assignee_email": "kirahoora@fastmail.com",  # Your email for testing
        "assignee_name": "Kira Hoora",
        "previous_values": {
            "status": "TODO",
            "priority": "MEDIUM", 
            "deadline": "2025-10-15"
        },
        "new_values": {
            "status": "IN_PROGRESS",
            "priority": "HIGH",
            "deadline": "2025-10-12"
        },
        "task_url": "http://localhost:8000/tasks/123"
    }
    
    print(f"📧 Sending notification for task: {test_data['task_title']}")
    print(f"👤 To: {test_data['assignee_email']}")
    print(f"🔄 Updated fields: {', '.join(test_data['updated_fields'])}")
    
    try:
        # Send the notification
        response = notification_service.notify_task_updated(
            task_id=test_data["task_id"],
            task_title=test_data["task_title"],
            updated_by=test_data["updated_by"],
            updated_fields=test_data["updated_fields"],
            assignee_email=test_data["assignee_email"],
            assignee_name=test_data["assignee_name"],
            previous_values=test_data["previous_values"],
            new_values=test_data["new_values"],
            task_url=test_data["task_url"]
        )
        
        # Display results
        if response.success:
            print("✅ SUCCESS: Email notification sent successfully!")
            print(f"📨 Message: {response.message}")
            print(f"👥 Recipients: {response.recipients_count}")
            print("\n📬 Check your FastMail inbox for the notification email!")
        else:
            print("❌ FAILED: Email notification failed!")
            print(f"💥 Error: {response.message}")
            
    except Exception as e:
        print(f"💥 ERROR: Exception occurred: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure you have created a .env file with your FastMail credentials")
        print("2. Check that your FastMail username and password are correct")
        print("3. Ensure you have internet connection")


def test_multiple_field_updates():
    """Test with different types of field updates"""
    
    print("\n" + "="*60)
    print("🔄 Testing multiple field update scenarios...")
    
    notification_service = get_notification_service()
    
    test_scenarios = [
        {
            "name": "Priority Change Only",
            "data": {
                "task_id": 124,
                "task_title": "Fix Bug in User Authentication",
                "updated_by": "System Admin",
                "updated_fields": ["Priority"],
                "assignee_email": "kirahoora@fastmail.com",
                "assignee_name": "Kira Hoora",
                "previous_values": {"priority": "LOW"},
                "new_values": {"priority": "CRITICAL"}
            }
        },
        {
            "name": "Status and Assignee Change",
            "data": {
                "task_id": 125,
                "task_title": "Design New Landing Page",
                "updated_by": "Project Manager",
                "updated_fields": ["Status", "Assignee"],
                "assignee_email": "kirahoora@fastmail.com",
                "assignee_name": "Kira Hoora",
                "previous_values": {"status": "TODO", "assignee": "John Doe"},
                "new_values": {"status": "IN_PROGRESS", "assignee": "Kira Hoora"}
            }
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📧 Test {i}: {scenario['name']}")
        
        try:
            response = notification_service.notify_task_updated(**scenario['data'])
            
            if response.success:
                print(f"✅ {scenario['name']} - Email sent successfully!")
            else:
                print(f"❌ {scenario['name']} - Failed: {response.message}")
                
        except Exception as e:
            print(f"💥 {scenario['name']} - Error: {str(e)}")


def main():
    """Main test function"""
    print("🎯 Kira Email Notification System Test")
    print("="*60)
    
    # Test basic notification
    test_task_update_notification()
    
    # Test multiple scenarios
    test_multiple_field_updates()
    
    print("\n" + "="*60)
    print("🏁 Test completed!")
    print("\n💡 Next steps:")
    print("1. Check your FastMail inbox for test emails")
    print("2. If successful, integrate notification_service.notify_task_updated() into your task update functions")
    print("3. If failed, check your .env file configuration")


if __name__ == "__main__":
    # Run the test
    main()
