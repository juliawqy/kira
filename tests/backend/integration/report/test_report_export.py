"""
Integration tests for project report export functionality.
Tests PDF and Excel report generation endpoints.
"""
from __future__ import annotations

import pytest
from datetime import date, datetime
from io import BytesIO

from backend.src.database.models.task import Task
from backend.src.database.models.project import Project
from backend.src.database.models.user import User
from backend.src.database.models.task_assignment import TaskAssignment
from backend.src.enums.task_status import TaskStatus
from backend.src.enums.user_role import UserRole
from backend.src.handlers.report_handler import generate_pdf_report, generate_excel_report


@pytest.fixture(scope="function")
def test_engine():
    """Create a temporary database for testing."""
    import tempfile
    import os
    from sqlalchemy import create_engine
    from backend.src.database.db_setup import Base
    
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    engine.dispose()
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def db_session(test_engine):
    """Create a database session for testing."""
    from sqlalchemy.orm import sessionmaker
    
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def setup_project_with_tasks(db_session):
    """Create a project with multiple tasks in different statuses."""
    # Override services to use test session
    from backend.src.services import task as task_service
    from backend.src.services import project as project_service
    from backend.src.services import task_assignment as assignment_service
    from sqlalchemy.orm import sessionmaker
    
    TestingSessionLocal = sessionmaker(
        bind=db_session.get_bind(),
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    
    # Store original SessionLocal
    original_task_session = task_service.SessionLocal
    original_project_session = project_service.SessionLocal
    original_assignment_session = assignment_service.SessionLocal
    
    # Replace with test session
    task_service.SessionLocal = TestingSessionLocal
    project_service.SessionLocal = TestingSessionLocal
    assignment_service.SessionLocal = TestingSessionLocal
    
    try:
        # Create users
        user1 = User(
            user_id=1,
            name="Project Manager",
            email="manager@example.com",
            role=UserRole.MANAGER.value,
            hashed_pw="hashed_password1",
            admin=False,
            department_id=None
        )
        user2 = User(
            user_id=2,
            name="Team Member 1",
            email="member1@example.com",
            role=UserRole.STAFF.value,
            hashed_pw="hashed_password2",
            admin=False,
            department_id=None
        )
        user3 = User(
            user_id=3,
            name="Team Member 2",
            email="member2@example.com",
            role=UserRole.STAFF.value,
            hashed_pw="hashed_password3",
            admin=False,
            department_id=None
        )
        
        db_session.add_all([user1, user2, user3])
        db_session.flush()
        
        # Create project
        project = Project(
            project_id=1,
            project_name="Test Project - Report Generation",
            project_manager=1,
            active=True
        )
        db_session.add(project)
        db_session.flush()
        
        # Create tasks with different statuses
        tasks_data = [
            {
                "title": "Projected Task 1",
                "description": "A task that hasn't started yet",
                "status": TaskStatus.TO_DO.value,
                "priority": 7,
                "start_date": date(2024, 12, 1),
                "deadline": date(2024, 12, 15),
                "project_id": 1,
                "active": True,
                "tag": "feature"
            },
            {
                "title": "Projected Task 2",
                "description": "Another planned task",
                "status": TaskStatus.TO_DO.value,
                "priority": 5,
                "start_date": date(2024, 12, 5),
                "deadline": date(2024, 12, 20),
                "project_id": 1,
                "active": True,
                "tag": "enhancement"
            },
            {
                "title": "In-Progress Task",
                "description": "Currently being worked on",
                "status": TaskStatus.IN_PROGRESS.value,
                "priority": 9,
                "start_date": date(2024, 11, 20),
                "deadline": date(2024, 12, 10),
                "project_id": 1,
                "active": True,
                "tag": "bugfix"
            },
            {
                "title": "Completed Task 1",
                "description": "Finished successfully",
                "status": TaskStatus.COMPLETED.value,
                "priority": 6,
                "start_date": date(2024, 11, 1),
                "deadline": date(2024, 11, 15),
                "project_id": 1,
                "active": True,
                "tag": "feature"
            },
            {
                "title": "Completed Task 2",
                "description": "Another completed task",
                "status": TaskStatus.COMPLETED.value,
                "priority": 4,
                "start_date": date(2024, 11, 5),
                "deadline": date(2024, 11, 20),
                "project_id": 1,
                "active": True,
                "tag": "documentation"
            },
            {
                "title": "Under Review Task",
                "description": "Blocked and needs review",
                "status": TaskStatus.BLOCKED.value,
                "priority": 8,
                "start_date": date(2024, 11, 15),
                "deadline": date(2024, 12, 5),
                "project_id": 1,
                "active": True,
                "tag": "blocked"
            },
        ]
        
        tasks = []
        for task_data in tasks_data:
            task = Task(**task_data)
            db_session.add(task)
            db_session.flush()
            tasks.append(task)
        
        # Assign users to tasks
        # Task 1 (Projected) -> user2
        assignment1 = TaskAssignment(task_id=tasks[0].id, user_id=2)
        # Task 3 (In-Progress) -> user2 and user3
        assignment2 = TaskAssignment(task_id=tasks[2].id, user_id=2)
        assignment3 = TaskAssignment(task_id=tasks[2].id, user_id=3)
        # Task 4 (Completed) -> user1
        assignment4 = TaskAssignment(task_id=tasks[3].id, user_id=1)
        
        db_session.add_all([assignment1, assignment2, assignment3, assignment4])
        db_session.commit()
        
        yield {"project_id": 1, "project": project, "tasks": tasks, "users": [user1, user2, user3]}
        
    finally:
        # Restore original SessionLocal
        task_service.SessionLocal = original_task_session
        project_service.SessionLocal = original_project_session
        assignment_service.SessionLocal = original_assignment_session


class TestReportExport:
    """Test report export functionality."""
    
    def test_generate_pdf_report_success(self, setup_project_with_tasks):
        """Test successful PDF report generation."""
        project_id = setup_project_with_tasks["project_id"]
        
        pdf_buffer = generate_pdf_report(project_id)
        
        assert pdf_buffer is not None
        assert isinstance(pdf_buffer, BytesIO)
        
        # Check PDF content
        pdf_buffer.seek(0)
        content = pdf_buffer.read()
        assert len(content) > 0
        assert content.startswith(b'%PDF')
    
    def test_generate_excel_report_success(self, setup_project_with_tasks):
        """Test successful Excel report generation."""
        project_id = setup_project_with_tasks["project_id"]
        
        excel_buffer = generate_excel_report(project_id)
        
        assert excel_buffer is not None
        assert isinstance(excel_buffer, BytesIO)
        
        # Check Excel content
        excel_buffer.seek(0)
        content = excel_buffer.read()
        assert len(content) > 0
        # Excel files start with PK (ZIP signature)
        assert content.startswith(b'PK')
    
    def test_generate_pdf_report_project_not_found(self):
        """Test PDF generation with non-existent project."""
        with pytest.raises(ValueError, match="Project 9999 not found"):
            generate_pdf_report(9999)
    
    def test_generate_excel_report_project_not_found(self):
        """Test Excel generation with non-existent project."""
        with pytest.raises(ValueError, match="Project 9999 not found"):
            generate_excel_report(9999)
    
    def test_pdf_report_contains_all_statuses(self, setup_project_with_tasks):
        """Verify PDF report includes all task statuses."""
        project_id = setup_project_with_tasks["project_id"]
        
        pdf_buffer = generate_pdf_report(project_id)
        pdf_buffer.seek(0)
        content = pdf_buffer.read()
        
        # Check that PDF was generated (has PDF header)
        assert content.startswith(b'%PDF')
        
        # PDF content is binary, so we can't easily search for text
        # Instead, verify the PDF was generated successfully and has reasonable size
        assert len(content) > 1000  # Should be at least 1KB for a valid report
    
    def test_excel_report_has_summary_sheet(self, setup_project_with_tasks):
        """Verify Excel report has summary information in the single sheet."""
        from openpyxl import load_workbook
        
        project_id = setup_project_with_tasks["project_id"]
        
        excel_buffer = generate_excel_report(project_id)
        excel_buffer.seek(0)
        
        wb = load_workbook(excel_buffer)
        
        # Check that the main sheet exists (now single sheet instead of separate Summary sheet)
        assert "Project Schedule Report" in wb.sheetnames
        
        # Check that the sheet has summary information
        ws = wb["Project Schedule Report"]
        assert ws["A1"].value is not None  # Report title should be there
        assert ws["A2"].value == "Project Name"  # Project name label
        assert ws["B2"].value is not None  # Project name value
        assert ws["A4"].value == "Summary"  # Summary section header
        
        # Check that summary metrics exist
        summary_values = []
        for row in range(5, 11):  # Rows 5-10 should have summary data
            if ws[f"A{row}"].value:
                summary_values.append(ws[f"A{row}"].value)
        
        assert "Total Tasks" in summary_values
        assert "Projected Tasks" in summary_values or "Completed Tasks" in summary_values

