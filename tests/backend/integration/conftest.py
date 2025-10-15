"""
Integration-specific fixtures to ensure db_session and task_factory are available
without relying on upstream conftest auto-discovery.
"""
from __future__ import annotations

import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.src.database.db_setup import Base
from backend.src.database.models.task import Task
from backend.src.enums.task_status import TaskStatus


@pytest.fixture(scope="session")
def test_engine_backend_integration():
	"""Create a temporary SQLite DB engine for backend integration tests."""
	db_fd, db_path = tempfile.mkstemp(suffix=".db")
	os.close(db_fd)

	engine = create_engine(f"sqlite:///{db_path}", echo=False)
	Base.metadata.create_all(bind=engine)

	yield engine

	if os.path.exists(db_path):
		os.remove(db_path)


@pytest.fixture
def db_session(test_engine_backend_integration):
	"""Provide a transaction-scoped session for each test."""
	connection = test_engine_backend_integration.connect()
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
def task_factory(db_session):
	"""Factory to create Task rows for integration tests."""
	def _create_task(**kwargs):
		default_data = {
			"title": "Test Task",
			"description": "Test Description",
			"status": TaskStatus.TO_DO.value,
			"priority": 5,
			"project_id": kwargs.pop("project_id", 1),
			"active": True,
		}
		default_data.update(kwargs)

		task = Task(**default_data)
		db_session.add(task)
		db_session.commit()
		db_session.refresh(task)
		return task

	return _create_task
