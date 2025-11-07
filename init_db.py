#!/usr/bin/env python
"""
Initialize database script.
This script will:
1. Create all database tables
2. Seed initial data (users, tasks, assignments, comments)

Usage:
    python init_db.py
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.src.database.db_setup_tables import engine, Base
from backend.src.init_scripts import seed_data
from backend.src.init_scripts import seed_demo_data

# seed_database = seed_data.seed_database
seed_database = seed_demo_data.seed_database

def main():
    """Initialize the database with tables and seed data."""
    print("=" * 60)
    print("KIRA Database Initialization")
    print("=" * 60)
    
    try:
        # Step 0: Drop all tables (for clean reset)
        print("\n🗑️  Step 0: Dropping all existing tables...")
        Base.metadata.drop_all(engine)
        print("✅ All tables dropped successfully!")
        
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
        print("  python -m uvicorn backend.src.main:app --reload")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

