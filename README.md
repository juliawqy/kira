# KIRA

## How to set up local kira.db
1. create local virtual environment 
    `python -m venv venv`
2. activate local environment
    windows: `venv\Scripts\activate`
    mac: `source venv/bin/activate`
3. install dependencies 
    `pip install -r requirements.txt`
4. database setup
    a. database file `kira.db` is located inside the `db/` folder
    b. to first set up the database
        `python db/db_setup_tables.py`
5. run project 
    `python main.py`
    a. currently `main.py` creates sample tasks
    b. for future operations, import helper functions in  `db/task_operations.py` for CRUD
        e.g. `from db.task_operations import create_task`
6. if you modify table structure (like `Task`), 
    a. delete old database
        windows: `del db\kira.db`
        mac: `rm db/kira.db`
    b. rerun table creation 
        `python db/db_setup_tables.py`

### Take note that the files in `.gitignore` are *NOT* to be pushed into git (venv, kira.db etc.)
7. to test out view all tasks function and view subtask function
    follow all the steps above until step 5