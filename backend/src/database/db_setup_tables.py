from backend.src.database.db_setup import engine, Base
from backend.src.database.models.task import Task
from backend.src.database.models.parent_assignment import ParentAssignment

# Create tables
Base.metadata.create_all(engine)
print("Tables created!")
