"""
Debug script to test FastMail SMTP connection
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import aiosmtplib
from email.mime.text import MIMEText


async def test_smtp_connection():
    """Test SMTP connection with detailed debugging"""
    
    print("🔧 FastMail SMTP Connection Test")
    print("=" * 50)
    
    # Get configuration from environment
    smtp_host = os.getenv('FASTMAIL_SMTP_HOST', 'smtp.fastmail.com')
    smtp_port = int(os.getenv('FASTMAIL_SMTP_PORT', '587'))
    username = os.getenv('FASTMAIL_USERNAME', '')
    password = os.getenv('FASTMAIL_PASSWORD', '')
    from_email = os.getenv('FASTMAIL_FROM_EMAIL', '')
    
    print(f"📧 SMTP Host: {smtp_host}")
    print(f"🔌 SMTP Port: {smtp_port}")
    print(f"👤 Username: {username}")
    print(f"📨 From Email: {from_email}")
    print(f"🔐 Password: {'✅ Set' if password else '❌ Missing'}")
    print()
    
    if not all([smtp_host, smtp_port, username, password, from_email]):
        print("❌ Missing required configuration!")
        print("Please check your .env file has all required fields:")
        print("- FASTMAIL_SMTP_HOST")
        print("- FASTMAIL_SMTP_PORT")
        print("- FASTMAIL_USERNAME")
        print("- FASTMAIL_PASSWORD")
        print("- FASTMAIL_FROM_EMAIL")
        return False
    
    try:
        print("🔄 Step 1: Creating SMTP connection...")
        
        # Create SMTP connection with detailed settings
        smtp = aiosmtplib.SMTP(
            hostname=smtp_host,
            port=smtp_port,
            use_tls=True,
            timeout=30,
            start_tls=False  # We'll call starttls manually
        )
        
        print("🔄 Step 2: Connecting to server...")
        await smtp.connect()
        print("✅ Connected to SMTP server!")
        
        print("🔄 Step 3: Starting TLS...")
        if smtp.port == 587:  # STARTTLS for port 587
            await smtp.starttls()
            print("✅ TLS started successfully!")
        
        print("🔄 Step 4: Authenticating...")
        await smtp.login(username, password)
        print("✅ Authentication successful!")
        
        print("🔄 Step 5: Sending test email...")
        
        # Create a simple test message
        msg = MIMEText("This is a test email from Kira Task Management System.")
        msg['Subject'] = "Kira SMTP Test"
        msg['From'] = from_email
        msg['To'] = from_email  # Send to yourself
        
        await smtp.send_message(msg, sender=from_email, recipients=[from_email])
        print("✅ Test email sent successfully!")
        
        print("🔄 Step 6: Closing connection...")
        await smtp.quit()
        print("✅ Connection closed!")
        
        print("\n🎉 All tests passed! Your FastMail configuration is working correctly.")
        print(f"📬 Check your inbox at {from_email} for the test email.")
        
        return True
        
    except aiosmtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your FastMail username and password are correct")
        print("2. Make sure you're using an App Password (not your main password)")
        print("3. Verify 2FA is enabled and you've generated an app password")
        return False
        
    except aiosmtplib.SMTPConnectError as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify FastMail SMTP settings (smtp.fastmail.com:587)")
        print("3. Check if your firewall/antivirus is blocking SMTP")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        print(f"📝 Full error details: {str(e)}")
        
        print("\n🔧 Common solutions:")
        print("1. Double-check all your .env configuration")
        print("2. Ensure you're using the correct FastMail app password")
        print("3. Try using port 465 with SSL instead of 587 with TLS")
        print("4. Check if your network blocks SMTP connections")
        
        return False


async def test_alternative_settings():
    """Test with alternative SMTP settings"""
    print("\n" + "=" * 50)
    print("🔄 Testing alternative SMTP settings (Port 465 with SSL)...")
    
    username = os.getenv('FASTMAIL_USERNAME', '')
    password = os.getenv('FASTMAIL_PASSWORD', '')
    from_email = os.getenv('FASTMAIL_FROM_EMAIL', '')
    
    try:
        # Try port 465 with SSL instead
        smtp = aiosmtplib.SMTP(
            hostname='smtp.fastmail.com',
            port=465,
            use_tls=True,
            timeout=30,
        )
        
        await smtp.connect()
        print("✅ Connected using port 465 with SSL!")
        
        await smtp.login(username, password)
        print("✅ Authentication successful on port 465!")
        
        await smtp.quit()
        print("✅ Alternative settings work! Consider updating your .env file to use port 465")
        
        return True
        
    except Exception as e:
        print(f"❌ Alternative settings also failed: {e}")
        return False


if __name__ == "__main__":
    print("Starting FastMail SMTP diagnostics...\n")
    
    async def main():
        success = await test_smtp_connection()
        
        if not success:
            print("\n" + "=" * 50) 
            print("Trying alternative settings...")
            await test_alternative_settings()
    
    asyncio.run(main())