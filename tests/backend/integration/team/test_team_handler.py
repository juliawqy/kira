# tests/backend/integration/team/test_team_handler.py
import pytest
import tempfile
import os
from sqlalchemy import create_engine, delete, text, select
from unittest.mock import patch
from sqlalchemy.orm import Session, sessionmaker
from backend.src.database.db_setup import Base
from backend.src.handlers import team_handler
from backend.src.services import team as team_service
from backend.src.services import user as user_service
from backend.src.services import task as task_service
from backend.src.services import task_assignment as assignment_service
from backend.src.database.models.team import Team
from backend.src.database.models.team_assignment import TeamAssignment
from backend.src.database.models.user import User
from backend.src.database.models.task import Task
from backend.src.database.models.task_assignment import TaskAssignment
from backend.src.database.models.department import Department
from backend.src.enums.task_status import TaskStatus
from backend.src.enums.user_role import UserRole
from tests.mock_data.team_data import (
    VALID_TEAM_CREATE,
    STAFF_USER,
    MANAGER_USER,
    NOT_FOUND_ID,
    DIRECTOR_USER,
)


@pytest.fixture(autouse=True)
def clean_db(test_engine):
    """Clean tables BEFORE each test"""
    TestingSession = sessionmaker(bind=test_engine, future=True)
    with TestingSession.begin() as s:
        s.execute(delete(TaskAssignment))
        s.execute(delete(TeamAssignment))
        s.execute(delete(Task))
        s.execute(delete(Team))
        s.execute(delete(User))
        s.execute(delete(Department))
    yield


@pytest.fixture(autouse=True)
def isolated_test_db():
    """Create isolated test database for integration tests."""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    test_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    
    # Enable foreign key constraints
    from sqlalchemy import event
    @event.listens_for(test_engine, "connect")
    def _fk_on(dbapi_connection, connection_record):
        cur = dbapi_connection.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()
    
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(bind=test_engine)

    with patch('backend.src.services.team.SessionLocal', TestSessionLocal), \
         patch('backend.src.services.user.SessionLocal', TestSessionLocal), \
         patch('backend.src.services.task.SessionLocal', TestSessionLocal), \
         patch('backend.src.services.task_assignment.SessionLocal', TestSessionLocal):
        yield test_engine
 
    test_engine.dispose()
    try:
        os.unlink(db_path)
    except (OSError, PermissionError):
        pass 


@pytest.fixture(autouse=True)
def seed_test_data(isolated_test_db):
    """Insert test data for integration tests."""
    TestingSession = sessionmaker(bind=isolated_test_db, future=True)
    
    with TestingSession.begin() as s:
        # Create users first (without department_id initially)
        manager = User(
            user_id=1,
            name="Test Manager",
            email="manager@test.com",
            role=UserRole.MANAGER.value,
            hashed_pw="hashed_password",
            department_id=None,
            admin=False
        )
        
        staff1 = User(
            user_id=2,
            name="Staff User 1",
            email="staff1@test.com",
            role=UserRole.STAFF.value,
            hashed_pw="hashed_password",
            department_id=None,
            admin=False
        )
        
        staff2 = User(
            user_id=3,
            name="Staff User 2",
            email="staff2@test.com",
            role=UserRole.STAFF.value,
            hashed_pw="hashed_password",
            department_id=None,
            admin=False
        )
        
        director = User(
            user_id=4,
            name="Test Director",
            email="director@test.com",
            role=UserRole.DIRECTOR.value,
            hashed_pw="hashed_password",
            department_id=None,
            admin=False
        )
        
        s.add_all([manager, staff1, staff2, director])
        s.flush()
        
        # Create department with manager reference
        dept = Department(department_name="Test Department", manager_id=manager.user_id)
        s.add(dept)
        s.flush()
        
        # Update users with department_id
        manager.department_id = dept.department_id
        staff1.department_id = dept.department_id
        staff2.department_id = dept.department_id
        director.department_id = dept.department_id
        s.flush()
        
        # Create team
        team = Team(
            team_id=1,
            team_name="Test Team",
            manager_id=manager.user_id,
            department_id=dept.department_id,
            team_number="01001"
        )
        s.add(team)
        s.flush()
        
        # Create task
        task = Task(
            id=1,
            title="Test Task",
            description="Test Description",
            status=TaskStatus.TO_DO.value,
            priority=5,
            active=True
        )
        s.add(task)
        s.flush()
    
    yield


class TestTeamHandlerIntegration:
    """Integration tests for team handler functionality."""

    def test_create_team_with_manager_success(self, isolated_test_db):
        """Test creating a team with manager assignment."""
        TestingSession = sessionmaker(bind=isolated_test_db, future=True)
        
        with TestingSession.begin() as session:
            # Get existing manager
            manager = session.get(User, 1)
            
            # Create new team
            team_data = team_handler.create_team_with_manager(
                team_name="New Team",
                manager_id=manager.user_id,
                department_id=1,
                team_number="02"
            )
            
            assert team_data["team_name"] == "New Team"
            assert team_data["manager_id"] == manager.user_id
            assert team_data["department_id"] == 1
            
            # Verify manager is assigned to team
            assignment = session.get(TeamAssignment, (team_data["team_id"], manager.user_id))
            assert assignment is not None

    def test_create_team_with_manager_invalid_role(self, isolated_test_db):
        """Test creating a team with non-manager user fails."""
        TestingSession = sessionmaker(bind=isolated_test_db, future=True)
        
        with TestingSession.begin() as session:
            staff_user = session.get(User, 2)
            
            with pytest.raises(ValueError, match="does not have permission to create teams"):
                team_handler.create_team_with_manager(
                    team_name="New Team",
                    manager_id=staff_user.user_id,
                    department_id=1,
                    team_number="02"
                )

    def test_get_team_with_members_success(self, isolated_test_db):
        """Test getting team with member details."""
        TestingSession = sessionmaker(bind=isolated_test_db, future=True)
        
        with TestingSession.begin() as session:
            # Assign members to team
            team_service.assign_users_to_team(1, [2, 3])
            
            # Get team with members
            team_data = team_handler.get_team_with_members(1)
            
            assert team_data["team_id"] == 1
            assert team_data["team_name"] == "Test Team"
            assert len(team_data["members"]) == 2
            
            member_ids = {member["user_id"] for member in team_data["members"]}
            assert member_ids == {2, 3}

    def test_assign_users_to_team_with_validation_success(self, isolated_test_db):
        """Test assigning users to team with proper validation."""
        TestingSession = sessionmaker(bind=isolated_test_db, future=True)
        
        with TestingSession.begin() as session:
            manager = session.get(User, 1)
            staff1 = session.get(User, 2)
            staff2 = session.get(User, 3)
            
            result = team_handler.assign_users_to_team_with_validation(
                team_id=1,
                user_ids=[staff1.user_id, staff2.user_id],
                assigner_id=manager.user_id
            )
            
            assert result["team_id"] == 1
            assert result["assigned_count"] == 2
            assert len(result["assigned_users"]) == 2
            
            # Verify assignments exist
            assignments = session.execute(
                select(TeamAssignment).where(TeamAssignment.team_id == 1)
            ).scalars().all()
            assert len(assignments) == 2

    def test_assign_users_to_team_with_validation_insufficient_permission(self, isolated_test_db):
        """Test assigning users to team without permission fails."""
        TestingSession = sessionmaker(bind=isolated_test_db, future=True)
        
        with TestingSession.begin() as session:
            staff1 = session.get(User, 2)
            staff2 = session.get(User, 3)
            
            with pytest.raises(ValueError, match="does not have permission to assign users"):
                team_handler.assign_users_to_team_with_validation(
                    team_id=1,
                    user_ids=[staff2.user_id],
                    assigner_id=staff1.user_id
                )

    def test_remove_users_from_team_with_validation_success(self, isolated_test_db):
        """Test removing users from team with proper validation."""
        TestingSession = sessionmaker(bind=isolated_test_db, future=True)
        
        with TestingSession.begin() as session:
            manager = session.get(User, 1)
            staff1 = session.get(User, 2)
            staff2 = session.get(User, 3)
            
            # First assign users
            team_service.assign_users_to_team(1, [staff1.user_id, staff2.user_id])
            
            # Then remove one user
            result = team_handler.remove_users_from_team_with_validation(
                team_id=1,
                user_ids=[staff1.user_id],
                remover_id=manager.user_id
            )
            
            assert result["team_id"] == 1
            assert result["removed_count"] == 1
            assert len(result["removed_users"]) == 1
            
            # Verify only one assignment remains
            assignments = session.execute(
                select(TeamAssignment).where(TeamAssignment.team_id == 1)
            ).scalars().all()
            assert len(assignments) == 1
            assert assignments[0].user_id == staff2.user_id

    def test_assign_team_to_task_with_notifications_success(self, isolated_test_db):
        """Test assigning team to task with notifications."""
        TestingSession = sessionmaker(bind=isolated_test_db, future=True)
        
        with TestingSession.begin() as session:
            manager = session.get(User, 1)
            staff1 = session.get(User, 2)
            staff2 = session.get(User, 3)
            
            # Assign users to team
            team_service.assign_users_to_team(1, [staff1.user_id, staff2.user_id])
            
            # Assign team to task
            result = team_handler.assign_team_to_task_with_notifications(
                team_id=1,
                task_id=1,
                assigner_id=manager.user_id
            )
            
            assert result["team_id"] == 1
            assert result["task_id"] == 1
            assert result["assigned_count"] == 2
            assert result["team_name"] == "Test Team"
            assert result["task_title"] == "Test Task"
            
            # Verify task assignments exist
            task_assignments = session.execute(
                select(TaskAssignment).where(TaskAssignment.task_id == 1)
            ).scalars().all()
            assert len(task_assignments) == 2
            assigned_user_ids = {ta.user_id for ta in task_assignments}
            assert assigned_user_ids == {staff1.user_id, staff2.user_id}

    def test_unassign_team_from_task_with_notifications_success(self, isolated_test_db):
        """Test unassigning team from task with notifications."""
        TestingSession = sessionmaker(bind=isolated_test_db, future=True)
        
        with TestingSession.begin() as session:
            manager = session.get(User, 1)
            staff1 = session.get(User, 2)
            staff2 = session.get(User, 3)
            
            # Assign users to team
            team_service.assign_users_to_team(1, [staff1.user_id, staff2.user_id])
            
            # Assign team to task
            assignment_service.assign_team_to_task(1, 1)
            
            # Unassign team from task
            result = team_handler.unassign_team_from_task_with_notifications(
                team_id=1,
                task_id=1,
                unassigner_id=manager.user_id
            )
            
            assert result["team_id"] == 1
            assert result["task_id"] == 1
            assert result["unassigned_count"] == 2
            
            # Verify task assignments are removed
            task_assignments = session.execute(
                select(TaskAssignment).where(TaskAssignment.task_id == 1)
            ).scalars().all()
            assert len(task_assignments) == 0

    def test_get_task_teams_with_details_success(self, isolated_test_db):
        """Test getting teams assigned to task with details."""
        TestingSession = sessionmaker(bind=isolated_test_db, future=True)
        
        with TestingSession.begin() as session:
            staff1 = session.get(User, 2)
            staff2 = session.get(User, 3)
            
            # Assign users to team
            team_service.assign_users_to_team(1, [staff1.user_id, staff2.user_id])
            
            # Assign team to task
            assignment_service.assign_team_to_task(1, 1)
            
            # Get task teams with details
            teams = team_handler.get_task_teams_with_details(1)
            
            assert len(teams) == 1
            team = teams[0]
            assert team["team_id"] == 1
            assert team["team_name"] == "Test Team"
            assert team["manager_id"] == 1
            assert team["manager_name"] == "Test Manager"
            assert team["member_count"] == 2

    def test_assign_multiple_teams_to_task_success(self, isolated_test_db):
        """Test assigning multiple teams to a task."""
        TestingSession = sessionmaker(bind=isolated_test_db, future=True)
        
        with TestingSession.begin() as session:
            manager = session.get(User, 1)
            staff1 = session.get(User, 2)
            staff2 = session.get(User, 3)
            
            # Create second team
            team2 = Team(
                team_id=2,
                team_name="Test Team 2",
                manager_id=manager.user_id,
                department_id=1,
                team_number="01002"
            )
            session.add(team2)
            session.flush()
            
            # Assign users to teams
            team_service.assign_users_to_team(1, [staff1.user_id])
            team_service.assign_users_to_team(2, [staff2.user_id])
            
            # Assign both teams to task
            result = team_handler.assign_multiple_teams_to_task(
                team_ids=[1, 2],
                task_id=1,
                assigner_id=manager.user_id
            )
            
            assert result["task_id"] == 1
            assert result["assigned_count"] == 2
            assert result["teams_assigned"] == 2
            assert result["notifications_sent"] == 2
            
            # Verify task assignments exist
            task_assignments = session.execute(
                select(TaskAssignment).where(TaskAssignment.task_id == 1)
            ).scalars().all()
            assert len(task_assignments) == 2

    def test_get_team_performance_summary_success(self, isolated_test_db):
        """Test getting team performance summary."""
        TestingSession = sessionmaker(bind=isolated_test_db, future=True)
        
        with TestingSession.begin() as session:
            staff1 = session.get(User, 2)
            staff2 = session.get(User, 3)
            
            # Assign users to team
            team_service.assign_users_to_team(1, [staff1.user_id, staff2.user_id])
            
            # Create additional tasks
            task2 = Task(
                id=2,
                title="Completed Task",
                description="Completed Description",
                status=TaskStatus.COMPLETED.value,
                priority=3,
                active=True
            )
            task3 = Task(
                id=3,
                title="Inactive Task",
                description="Inactive Description",
                status=TaskStatus.TO_DO.value,
                priority=7,
                active=False
            )
            session.add_all([task2, task3])
            session.flush()
            
            # Assign tasks to team members
            assignment_service.assign_users(task2.id, [staff1.user_id])
            assignment_service.assign_users(task3.id, [staff2.user_id])
            
            # Get performance summary
            performance = team_handler.get_team_performance_summary(1)
            
            assert performance["team_id"] == 1
            assert performance["team_name"] == "Test Team"
            assert performance["member_count"] == 2
            assert performance["total_tasks"] == 2  # Only active tasks
            assert performance["completed_tasks"] == 1
            assert performance["active_tasks"] == 1
            assert performance["completion_rate"] == 50.0

    def test_get_user_team_workload_success(self, isolated_test_db):
        """Test getting user team workload."""
        TestingSession = sessionmaker(bind=isolated_test_db, future=True)
        
        with TestingSession.begin() as session:
            staff1 = session.get(User, 2)
            
            # Assign user to team
            team_service.assign_users_to_team(1, [staff1.user_id])
            
            # Create additional tasks
            task2 = Task(
                id=2,
                title="High Priority Task",
                description="High Priority Description",
                status=TaskStatus.TO_DO.value,
                priority=9,
                active=True
            )
            session.add(task2)
            session.flush()
            
            # Assign tasks to user
            assignment_service.assign_users(1, [staff1.user_id])
            assignment_service.assign_users(2, [staff1.user_id])
            
            # Get user workload
            workload = team_handler.get_user_team_workload(staff1.user_id)
            
            assert workload["user_id"] == staff1.user_id
            assert workload["user_name"] == "Staff User 1"
            assert workload["total_teams"] == 1
            assert workload["total_active_tasks"] == 2
            assert len(workload["team_workloads"]) == 1
            
            team_workload = workload["team_workloads"][0]
            assert team_workload["team_id"] == 1
            assert team_workload["team_name"] == "Test Team"
            assert team_workload["task_count"] == 2
            assert team_workload["high_priority_tasks"] == 1

    def test_list_teams_with_member_counts_success(self, isolated_test_db):
        """Test listing teams with member counts."""
        TestingSession = sessionmaker(bind=isolated_test_db, future=True)
        
        with TestingSession.begin() as session:
            staff1 = session.get(User, 2)
            staff2 = session.get(User, 3)
            
            # Assign users to team
            team_service.assign_users_to_team(1, [staff1.user_id, staff2.user_id])
            
            # List teams with counts
            teams = team_handler.list_teams_with_member_counts()
            
            assert len(teams) == 1
            team = teams[0]
            assert team["team_id"] == 1
            assert team["team_name"] == "Test Team"
            assert team["member_count"] == 2

    def test_get_user_teams_success(self, isolated_test_db):
        """Test getting teams for a user."""
        TestingSession = sessionmaker(bind=isolated_test_db, future=True)
        
        with TestingSession.begin() as session:
            staff1 = session.get(User, 2)
            
            # Assign user to team
            team_service.assign_users_to_team(1, [staff1.user_id])
            
            # Get user teams
            teams = team_handler.get_user_teams(staff1.user_id)
            
            assert len(teams) == 1
            team = teams[0]
            assert team["team_id"] == 1
            assert team["team_name"] == "Test Team"
            assert team["manager_id"] == 1
