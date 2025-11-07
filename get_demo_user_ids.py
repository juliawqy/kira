#!/usr/bin/env python
"""Helper script to get demo user IDs from the database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.src.database.db_setup import SessionLocal
from backend.src.database.models import user, department, task, task_assignment, comment, project, team, team_assignment, parent_assignment

def get_demo_user_ids():
    """Get user IDs for the 6 demo users."""
    with SessionLocal() as session:
        # Staff 1: Account Manager - Aisha Rahman
        staff1 = session.query(user.User).filter(user.User.email == "aisha.rahman.sales@kira.ai").first()
        
        # Staff 2: IT Member - Aaron Koh
        staff2 = session.query(user.User).filter(user.User.email == "aaron.koh.it@kira.ai").first()
        
        # Manager 1: Sales Manager - Alice Tan
        manager1 = session.query(user.User).filter(user.User.email == "alice.tan.sales@kira.ai").first()
        
        # Manager 2: Finance Manager - Ivan Lee
        manager2 = session.query(user.User).filter(user.User.email == "ivan.lee.fin@kira.ai").first()
        
        # Director 1: Sales Director - Derek Tan
        director1 = session.query(user.User).filter(user.User.email == "derek.tan.sales@kira.ai").first()
        
        # Director 2: HR Director - Sally Loh
        director2 = session.query(user.User).filter(user.User.email == "sally.loh.hr@kira.ai").first()
        
        print("=" * 60)
        print("DEMO USER IDs FOR FRONTEND")
        print("=" * 60)
        if staff1:
            print(f"Staff 1 (Account Manager): user_id = {staff1.user_id}, name = {staff1.name}")
        if staff2:
            print(f"Staff 2 (IT Member): user_id = {staff2.user_id}, name = {staff2.name}")
        if manager1:
            print(f"Manager 1 (Sales Manager): user_id = {manager1.user_id}, name = {manager1.name}")
        if manager2:
            print(f"Manager 2 (Finance Manager): user_id = {manager2.user_id}, name = {manager2.name}")
        if director1:
            print(f"Director 1 (Sales Director): user_id = {director1.user_id}, name = {director1.name}")
        if director2:
            print(f"Director 2 (HR Director): user_id = {director2.user_id}, name = {director2.name}")
        print("=" * 60)
        
        return {
            'staff1': staff1.user_id if staff1 else None,
            'staff2': staff2.user_id if staff2 else None,
            'manager1': manager1.user_id if manager1 else None,
            'manager2': manager2.user_id if manager2 else None,
            'director1': director1.user_id if director1 else None,
            'director2': director2.user_id if director2 else None,
        }

if __name__ == "__main__":
    get_demo_user_ids()

