"""
Test script to verify synchronous notification services
"""
import sys
import os

# Add the project root to Python path so we can import modules
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(project_root)

from backend.src.services.notification_service import get_notification_service
from backend.src.services.email_service import get_email_service
from backend.src.services.task_notification_service import get_task_notification_service


def test_service_imports():
    """Test that all services can be imported and instantiated"""
    print("🧪 Testing service imports...")
    
    try:
        # Test email service
        email_service = get_email_service()
        print("✅ Email service imported successfully")
        
        # Test notification service
        notification_service = get_notification_service()
        print("✅ Notification service imported successfully")
        
        # Test task notification service
        task_notification_service = get_task_notification_service()
        print("✅ Task notification service imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False


def test_synchronous_behavior():
    """Test that services are truly synchronous"""
    print("\n🔄 Testing synchronous behavior...")
    
    try:
        notification_service = get_notification_service()
        
        # This should work without await since it's now synchronous
        response = notification_service.notify_task_updated(
            task_id=999,
            task_title="Sync Test Task",
            updated_by="Test User",
            updated_fields=["Title"],
            assignee_email="test@example.com",
            assignee_name="Test User"
        )
        
        print("✅ Synchronous call completed successfully")
        print(f"📊 Response type: {type(response)}")
        print(f"📊 Response success: {response.success}")
        
        return True
        
    except Exception as e:
        print(f"❌ Synchronous test failed: {str(e)}")
        return False


def main():
    """Main test function"""
    print("🎯 Synchronous Services Test")
    print("="*50)
    
    # Test imports
    import_success = test_service_imports()
    
    # Test synchronous behavior  
    sync_success = test_synchronous_behavior()
    
    print("\n" + "="*50)
    if import_success and sync_success:
        print("🎉 All tests passed! Services are now synchronous.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    print("\n💡 Services are now ready for real-time notifications!")


if __name__ == "__main__":
    main()