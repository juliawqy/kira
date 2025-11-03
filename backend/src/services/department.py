# backend/src/services/department.py
from typing import Optional
from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.department import Department
from backend.src.enums.user_role import UserRole

def add_department(name, manager, description=None, created_at=None, user_role=UserRole.HR):
    if user_role != UserRole.HR:
        raise PermissionError("Only HR can create a department.")
    if not name or not str(name).strip():
        raise ValueError("Department name cannot be empty.")
    if manager is None or (isinstance(manager, str) and not manager.strip()):
        raise ValueError("Manager cannot be empty.")

    with SessionLocal() as db:
        try:
            dept = Department(
                department_name=str(name).strip(),
                manager_id=int(manager),
            )
            db.add(dept)
            db.commit()
            db.refresh(dept)
            return dept
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
    
def get_department_by_director(director_id: int) -> Optional[dict]:
    with SessionLocal() as db:
        dept = (
            db.query(Department)
              .filter(Department.manager_id == director_id)
              .first()
        )
        if not dept:
            return None
        return {
            "department_id": dept.department_id,
            "department_name": dept.department_name,
            "manager_id": dept.manager_id,
        }
