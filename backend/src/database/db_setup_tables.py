from backend.src.database.db_setup import engine, Base
from backend.src.database.models.task import Task
from backend.src.database.models.project import Project, ProjectAssignment
from backend.src.database.models.user import User
from backend.src.database.models.team import Team
from backend.src.database.models.user import User
from backend.src.database.models.department import Department


# Create tables
Base.metadata.create_all(engine)
print("Tables created!")
