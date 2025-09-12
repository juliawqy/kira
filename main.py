
from db.task_operations import add_task, update_task, assign_task
from db.db_setup import SessionLocal
from models.task import Task
from datetime import date

# Add parent task
parent_id = add_task(
    title="Launch Project",
    description="Initial project launch tasks",
    start_date=date(2025, 9, 9),
    deadline=date(2025, 9, 30),
    priority="High",
    status="To-do",
    collaborators="Julia,Alex",
    notes="Kickoff meeting on Monday"
)

# Add subtask linked to parent
subtask_id = add_task(
    title="Prepare slides",
    description="Create presentation slides",
    start_date=date(2025, 9, 10),
    deadline=date(2025, 9, 12),
    parent_id=parent_id,
    status="To-do",
    priority="Medium"
)

print("Tasks created successfully!\n")

# --- PRINT ALL TASKS (before updates) ---

with SessionLocal() as session:
    parent_tasks = session.query(Task).filter(Task.parent_id == None).all()
    for t in parent_tasks:
        print(f"Parent Task: {t.title} | Status: {t.status} | Priority: {t.priority} | Assigned to: {t.collaborators}")
        subtasks = session.query(Task).filter(Task.parent_id == t.id).all()
        for st in subtasks:
            print(f"  Subtask: {st.title} | Status: {st.status} | Priority: {st.priority} | Assigned to: {st.collaborators}")


# --- PERFORM UPDATES ---
# Update just a couple of fields on the parent
updated_parent = update_task(
    parent_id,
    status="In-progress",
    notes="Kickoff complete; waiting on assets"
)

updated_subtask = update_task(
    subtask_id,
    status="Done",
    deadline=date(2025, 9, 11) 
)


# --- PRINT ALL TASKS (after updates) ---
print("\nAfter updates:")
with SessionLocal() as session:
    parent_tasks = session.query(Task).filter(Task.parent_id == None).all()
    for t in parent_tasks:
        print(f"Parent Task: {t.title} | Status: {t.status} | Priority: {t.priority} | Notes: {t.notes}")
        subtasks = session.query(Task).filter(Task.parent_id == t.id).all()
        for st in subtasks:
            print(f"  Subtask: {st.title} | Status: {st.status} | Priority: {st.priority} | Deadline: {st.deadline}")

