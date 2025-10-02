"""
Global test configuration and fixtures.
"""
import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.database.db_setup import Base
from backend.src.database.models.user import User
from backend.src.database.models.task import Task


@pytest.fixture(scope="session")
def test_engine():
    """
    Create a test database engine for the entire test session.
    """
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup: Remove temporary database
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def db_session(test_engine):
    """
    Create a database session for each test with automatic rollback.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def user_factory(db_session):
    """
    Factory for creating test users.
    """
    def _create_user(**kwargs):
        from backend.src.enums.user_role import UserRole
        default_data = {
            "name": "Test User",
            "email": "test@example.com", 
            "role": UserRole.STAFF,
            "password_hash": "hashed_password",
            "department_id": 1,
            "is_admin": False
        }
        default_data.update(kwargs)
        
        user = User(**default_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    return _create_user


@pytest.fixture
def task_factory(db_session):
    """
    Factory for creating test tasks.
    """
    def _create_task(**kwargs):
        from backend.src.enums.task_status import TaskStatus
        from backend.src.enums.task_priority import TaskPriority
        default_data = {
            "title": "Test Task",
            "description": "Test Description",
            "status": TaskStatus.TODO,
            "priority": TaskPriority.MEDIUM,
            "assigned_user_id": None
        }
        default_data.update(kwargs)
        
        task = Task(**default_data)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        return task
    
    return _create_task
