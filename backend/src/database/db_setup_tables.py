from database.db_setup import engine, Base
from database.models.task import Task
from database.models.parent_assignment import ParentAssignment

# Create tables
Base.metadata.create_all(engine)
print("Tables created!")
