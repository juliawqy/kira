from typing import Optional
from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.department import Department
from backend.src.enums.user_role import UserRole

# Alias for test compatibility
def add_department(**kwargs):
	return create_department(**kwargs)
from typing import Optional
from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.department import Department
from backend.src.enums.user_role import UserRole


# Accepts keyword arguments for compatibility with test and mock data
def create_department(name, manager, description=None, created_at=None, user_role=UserRole.HR):
	if user_role != UserRole.HR:
		raise PermissionError("Only HR can create a department.")
	if not name or not str(name).strip():
		raise ValueError("Department name cannot be empty.")
	if not manager or not str(manager).strip():
		raise ValueError("Manager cannot be empty.")
	db = SessionLocal()
	try:
		department = Department(
			name=name,
			main=description,
			manager_id=manager
		)
		db.add(department)
		db.commit()
		db.refresh(department)
		return department
	except Exception as e:
		db.rollback()
		raise e
	finally:
		db.close()
		
#creating a function that gets a department by id
def get_department_by_id(department_id: int) -> Optional[Department]:
	db = SessionLocal()
	try:
		department = db.query(Department).filter(Department.id == department_id).first()
		if department:
			return {
				"id": department.id,
				"name": getattr(department, "name", None),
				"main": getattr(department, "main", None),
				"manager_id": getattr(department, "manager_id", None)
			}
		return None
	except Exception as e:
		raise e
	finally:
		db.close()