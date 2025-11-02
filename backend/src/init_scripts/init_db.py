"""
Initialize database script.
This script will:
1. Create all database tables
2. Seed initial data (users, tasks, assignments, comments)

Usage:
    python -m backend.src.init_scripts.init_db
"""

import sys
from pathlib import Path

# Add project root to path so we can import backend modules
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.src.database.db_setup_tables import engine, Base
from backend.src.init_scripts.seed_data import seed_database

def init_database():
    """Initialize the database with tables and seed data."""
    print("=" * 60)
    print("KIRA Database Initialization")
    print("=" * 60)
    
    try:
        # Step 1: Create tables
        print("\n📋 Step 1: Creating database tables...")
        Base.metadata.create_all(engine)
        print("✅ Tables created successfully!")
        
        # Step 2: Seed data
        print("\n🌱 Step 2: Seeding initial data...")
        seed_database()
        
        print("\n" + "=" * 60)
        print("✅ Database initialization completed successfully!")
        print("=" * 60)
        print("\nYou can now run the backend server:")
        print("  cd backend && python -m uvicorn src.main:app --reload")
        print("\nDefault users:")
        print("  - Cong (Staff): cong@example.com / Password123!")
        print("  - Julia (Staff): julia@example.com / Password123!")
        print("  - Manager1: manager@example.com / Password123!")
        print("  - Director1: director@example.com / Password123!")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()

