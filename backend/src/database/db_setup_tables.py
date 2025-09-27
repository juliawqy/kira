from backend.src.database.db_setup import engine, Base
from backend.src.database.models.task import Task
from backend.src.database.models.team import Team

# Create tables
Base.metadata.create_all(engine)
print("Tables created!")
