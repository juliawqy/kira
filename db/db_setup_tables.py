from db.db_setup import engine, Base
from models.task import Task

# Create tables
Base.metadata.create_all(engine)
print("Tables created!")
