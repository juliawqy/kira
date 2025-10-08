"""
Setup script to create .env file from .env.example
"""
import shutil
import os

def setup_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    
    env_example_path = ".env.example"
    env_path = ".env"
    
    if os.path.exists(env_path):
        print(f"✅ {env_path} already exists")
        return True
    
    if not os.path.exists(env_example_path):
        print(f"❌ {env_example_path} not found!")
        return False
    
    try:
        shutil.copy2(env_example_path, env_path)
        print(f"✅ Created {env_path} from {env_example_path}")
        print(f"📝 Your FastMail credentials are already configured in the file")
        return True
    except Exception as e:
        print(f"❌ Failed to create {env_path}: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Setting up environment configuration...")
    setup_env_file()