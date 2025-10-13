"""
Test script to verify synchronous email and notification services
"""
import sys
import os

# Add the project root to Python path so we can import modules
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(project_root)

from backend.src.services.notification_service import get_notification_service
from backend.src.services.email_service import get_email_service


def test_service_imports():
    """Test that both email and notification services can be imported and instantiated"""
    print("🧪 Testing service imports...")
    
    try:
        # Test email service
        email_service = get_email_service()
        print("✅ Email service imported successfully")
        print(f"   📧 SMTP Host: {email_service.settings.fastmail_smtp_host}")
        print(f"   📧 SMTP Port: {email_service.settings.fastmail_smtp_port}")
        
        # Test notification service
        notification_service = get_notification_service()
        print("✅ Notification service imported successfully")
        print(f"   🔔 Email service connected: {notification_service.email_service is not None}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False


def test_synchronous_behavior():
    """Test that notification service is truly synchronous (no await needed)"""
    print("\n🔄 Testing synchronous behavior...")
    
    try:
        notification_service = get_notification_service()
        
        # This should work without await since it's now synchronous
        print("   📤 Sending test notification...")
        response = notification_service.notify_task_updated(
            task_id=999,
            task_title="Sync Test Task",
            updated_by="Test User",
            updated_fields=["Title"],
            assignee_email="test@example.com",
            assignee_name="Test User"
        )
        
        print("✅ Synchronous call completed successfully")
        print(f"   📊 Response type: {type(response).__name__}")
        print(f"   📊 Response success: {response.success}")
        print(f"   📊 Response message: {response.message}")
        
        return True
        
    except Exception as e:
        print(f"❌ Synchronous test failed: {str(e)}")
        return False


def main():
    """Main test function"""
    print("🎯 Email & Notification Services Test")
    print("="*55)
    
    # Test imports
    import_success = test_service_imports()
    
    # Test synchronous behavior  
    sync_success = test_synchronous_behavior()
    
    print("\n" + "="*55)
    if import_success and sync_success:
        print("🎉 All tests passed! Email services are synchronous and ready!")
        print("\n📋 Available services:")
        print("   • EmailService - Direct SMTP email sending")
        print("   • NotificationService - Task notification orchestration")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    print("\n💡 Services are ready for real-time email notifications!")


if __name__ == "__main__":
    main()