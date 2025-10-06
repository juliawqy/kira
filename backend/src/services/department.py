from __future__ import annotations

from typing import Optional, Iterable

from sqlalchemy import nulls_last, select
from sqlalchemy.orm import selectinload

from backend.src.database.db_setup import SessionLocal
from backend.src.database.models.department import Department



def _normalize_members(members: Optional[Iterable[str]]) -> list[str]:
    """Strip, dedupe, sort member names."""
    if not members:
        return []
    cleaned = {m.strip() for m in members if m and m.strip()}
    return sorted(cleaned)


def _csv_to_list(csv: Optional[str]) -> list[str]:
    return _normalize_members(csv.split(",")) if csv else []


def _list_to_csv(members: Iterable[str]) -> str:
    return ",".join(_normalize_members(members))


def add_department(
    name: str,
    description: Optional[str] = None,
    head: Optional[str] = None,
    members: Optional[str] = None,
    notes: Optional[str] = None,
    parent_id: Optional[int] = None,
) -> Department:
    """Create a department and return it."""
    if not name or not name.strip():
        raise ValueError("Department name cannot be empty")

    members_csv = _list_to_csv(_csv_to_list(members))
    with SessionLocal.begin() as session:
        dept = Department(
            name=name.strip(),
            description=description,
            head=head,
            members=members_csv,
            notes=notes,
            parent_id=parent_id,
        )
        session.add(dept)
        session.flush()
        session.refresh(dept)
        return dept


def get_department_with_subdepartments(department_id: int):
    """Get a department and its subdepartments."""
    with SessionLocal() as session:
        stmt = (
            select(Department)
            .where(Department.id == department_id)
            .options(selectinload(Department.subdepartments))
        )
        return session.execute(stmt).scalar_one_or_none()


def list_parent_departments():
    """List all top-level departments with their subdepartments."""
    with SessionLocal() as session:
        stmt = (
            select(Department)
            .where(Department.parent_id.is_(None))
            .options(selectinload(Department.subdepartments))
            .order_by(nulls_last(Department.name.asc()), Department.id.asc())
        )
        return session.execute(stmt).scalars().all()



def update_department(
    department_id: int,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    head: Optional[str] = None,
    members: Optional[str] = None,
    notes: Optional[str] = None,
    parent_id: Optional[int] = None,
) -> Optional[Department]:
    """Update department fields; return updated department or None."""
    with SessionLocal.begin() as session:
        dept = session.get(Department, department_id)
        if dept is None:
            return None

        if name is not None:
            dept.name = name.strip()
        if description is not None:
            dept.description = description
        if head is not None:
            dept.head = head.strip()
        if members is not None:
            dept.members = _list_to_csv(_csv_to_list(members))
        if notes is not None:
            dept.notes = notes
        if parent_id is not None:
            dept.parent_id = parent_id

        session.add(dept)
        session.flush()
        session.refresh(dept)
        return dept


def assign_members(department_id: int, new_members: list[str]) -> Department:
    """Assign members and return updated department."""
    with SessionLocal.begin() as session:
        dept = session.get(Department, department_id)
        if not dept:
            raise ValueError("Department not found")

        existing = _csv_to_list(dept.members)
        updated = _normalize_members([*existing, *new_members])
        dept.members = _list_to_csv(updated)

        session.add(dept)
        session.flush()
        session.refresh(dept)
        return dept


def unassign_members(department_id: int, members_to_remove: list[str]) -> Department:
    """Unassign members and return updated department."""
    with SessionLocal.begin() as session:
        dept = session.get(Department, department_id)
        if not dept:
            raise ValueError("Department not found")

        existing = set(_csv_to_list(dept.members))
        updated = sorted(existing - set(_normalize_members(members_to_remove)))
        dept.members = _list_to_csv(updated) if updated else None

        session.add(dept)
        session.flush()
        session.refresh(dept)
        return dept


def delete_subdepartment(subdepartment_id: int) -> bool:
    """Delete a subdepartment; return True if deleted, False if not found."""
    with SessionLocal.begin() as session:
        sub = session.get(Department, subdepartment_id)
        if sub is None:
            return False
        if sub.parent_id is None:
            raise ValueError(f"Department {subdepartment_id} is not a subdepartment (no parent). Use delete_department().")
        session.delete(sub)
        return True


def delete_department(department_id: int) -> dict:
    """Delete a department and detach its subdepartments; return {'deleted': id, 'subdepartments_detached': n}."""
    with SessionLocal.begin() as session:
        dept = session.get(Department, department_id)
        if dept is None:
            raise ValueError(f"Department id {department_id} not found")

        detached = 0
        if hasattr(dept, "subdepartments"):
            for sub in list(dept.subdepartments):
                sub.parent_id = None
                detached += 1
        else:
            subs = session.execute(select(Department).where(Department.parent_id == department_id)).scalars().all()
            for sub in subs:
                sub.parent_id = None
                detached += 1

        session.flush()
        session.delete(dept)
        return {"deleted": department_id, "subdepartments_detached": detached}
