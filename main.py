from db.task_operations import add_task, update_task, list_parent_tasks, get_task_with_subtasks

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

# --- Function for KIRA-1 Testing  ---
with SessionLocal() as session:
    parent_tasks = session.query(Task).filter(Task.parent_id == None).all()
    for t in parent_tasks:
        print(f"Parent Task: {t.title} | Status: {t.status} | Priority: {t.priority} | Assigned to: {t.collaborators}")
        subtasks = session.query(Task).filter(Task.parent_id == t.id).all()
        for st in subtasks:
            print(f"  Subtask: {st.title} | Status: {st.status} | Priority: {st.priority} | Assigned to: {st.collaborators}")

# --- Function for KIRA-2 Testing ---
def show_task_details(task, indent=""):
    print(f"{indent}ID: {task.id}")
    print(f"{indent}Title: {task.title}")
    print(f"{indent}Description: {task.description or '-'}")
    print(f"{indent}Start date: {task.start_date or '-'}")
    print(f"{indent}Deadline: {task.deadline or '-'}")
    print(f"{indent}Notes: {task.notes or '-'}")
    print(f"{indent}Comments: {task.comments or '-'}")
    print(f"{indent}Collaborators: {task.collaborators or '-'}")
    print(f"{indent}Status: {task.status}")
    print(f"{indent}Priority: {task.priority}")

print("\n=== TEST list_parent_tasks() ===")
parents = list_parent_tasks()
for t in parents:
    print("\nParent Task:")
    show_task_details(t, indent="  ")
    if getattr(t, "subtasks", None):
        print("  Subtasks:")
        for st in t.subtasks:
            show_task_details(st, indent="    ")
    else:
        print("  Subtasks: (none)")

print("\n=== TEST get_task_with_subtasks(parent_id=1) ===")
task = get_task_with_subtasks(1)  # explicitly fetch parent task with ID 1
if task:
    if getattr(task, "subtasks", None):
        print(f"\nSubtasks of '{task.title}':")
        for st in task.subtasks:
            show_task_details(st, indent="  ")
    else:
        print(f"\nParent task '{task.title}' has no subtasks.")
else:
    print("No task found with ID=1")

# --- Function for KIRA-3 Testing ---
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

# --- Function for KIRA-3 Testing ---
print("\nAfter updates:")
with SessionLocal() as session:
    parent_tasks = session.query(Task).filter(Task.parent_id == None).all()
    for t in parent_tasks:
        print(f"Parent Task: {t.title} | Status: {t.status} | Priority: {t.priority} | Notes: {t.notes}")
        subtasks = session.query(Task).filter(Task.parent_id == t.id).all()
        for st in subtasks:
            print(f"  Subtask: {st.title} | Status: {st.status} | Priority: {st.priority} | Deadline: {st.deadline}")

