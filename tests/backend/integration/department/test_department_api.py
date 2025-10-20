# tests/backend/integration/department/test_department_integration.py
import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.src.database.db_setup import Base
from backend.src.services import department as dept_service
from backend.src.database.models.department import Department
from tests.mock_data.department_data import (
    VALID_ADD_DEPARTMENT,
    VALID_DEPARTMENT_1,
    INVALID_DEPARTMENT_NO_NAME,
    INVALID_DEPARTMENT_NO_MANAGER,
    INVALID_DEPARTMENT_NON_HR,
)

from unittest.mock import patch


@pytest.fixture(autouse=True)
def isolated_test_db():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    test_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine)
    with patch("backend.src.services.department.SessionLocal", TestSessionLocal):
        yield test_engine
    test_engine.dispose()
    try:
        os.unlink(db_path)
    except (OSError, PermissionError):
        pass


# INT-067/001
def test_create_and_get_department(isolated_test_db):
    dept_obj = dept_service.add_department(**VALID_ADD_DEPARTMENT)

    # add_department returns the ORM object
    assert dept_obj.department_name == VALID_DEPARTMENT_1["department_name"]
    assert dept_obj.manager_id == VALID_DEPARTMENT_1["manager_id"]
    assert getattr(dept_obj, "department_id", None) is not None

    # Now fetch via service
    fetched = dept_service.get_department_by_id(dept_obj.department_id)
    assert fetched is not None
    assert fetched["department_id"] == dept_obj.department_id
    assert fetched["department_name"] == dept_obj.department_name
    assert fetched["manager_id"] == dept_obj.manager_id


# INT-067/002
@pytest.mark.parametrize("invalid_payload", [INVALID_DEPARTMENT_NO_NAME, INVALID_DEPARTMENT_NO_MANAGER])
def test_create_department_validation_errors(isolated_test_db, invalid_payload):
    with pytest.raises(ValueError):
        dept_service.add_department(**invalid_payload)


# INT-067/003
def test_create_department_permission_denied(isolated_test_db):
    with pytest.raises(PermissionError):
        dept_service.add_department(**INVALID_DEPARTMENT_NON_HR)


# INT-069/001
def test_get_department_not_found(isolated_test_db):
    result = dept_service.get_department_by_id(9999)
    assert result is None


# INT-069/002
def test_department_row_persisted_in_db(isolated_test_db):
    dept_obj = dept_service.add_department(**VALID_ADD_DEPARTMENT)

    sess = Session(bind=isolated_test_db)
    try:
        row = (
            sess.query(Department)
            .filter(
                Department.department_id == dept_obj.department_id,
                Department.department_name == dept_obj.department_name,
                Department.manager_id == dept_obj.manager_id,
            )
            .one_or_none()
        )
        assert row is not None
    finally:
        sess.close()
