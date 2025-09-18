from database.db_setup import engine, Base
from database.models.task import Task

# Create tables
Base.metadata.create_all(engine)
print("Tables created!")
