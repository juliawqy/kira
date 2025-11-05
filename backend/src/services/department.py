# backend/src/services/department.py
from typing import Optional
from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.department import Department
from backend.src.enums.user_role import UserRole

def add_department(name, manager):

    with SessionLocal() as db:
        try:
            dept = Department(
                department_name=str(name).strip(),
                manager_id=int(manager),
            )
            db.add(dept)
            db.commit()
            db.refresh(dept)
            return {
                "department_id": dept.department_id,
                "department_name": dept.department_name,
                "manager_id": dept.manager_id,
            }
        except Exception:
            db.rollback()
            raise

def get_department_by_id(department_id: int) -> Optional[dict]:
    with SessionLocal() as db:
        dept = (
            db.query(Department)
              .filter(Department.department_id == department_id)
              .first()
        )
        if not dept:
            return None
        return {
            "department_id": dept.department_id,
            "department_name": dept.department_name,
            "manager_id": dept.manager_id,
        }
