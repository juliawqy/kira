# KIRA

## How to set up local kira.db
1. create local virtual environment 
    `python -m venv venv`

2. activate local environment
    windows: `venv\Scripts\activate`
    mac: `source venv/bin/activate`

3. install dependencies 
    `pip install -r requirements.txt`

4. put backend on the import part
    windows: `set PYTHONPATH=C:\wamp64\www\kira\backend\src`
    mac: `export PYTHONPATH=backend/src`

5. Create database and setup tables (SQLite)
    `python -m database.db_setup_tables`

5. run project 
    `uvicorn main:app --app-dir backend/src --reload`
    Access swagger docs: http://localhost:8000/docs

6. if you modify table structure (like `Task`), 
    a. delete old database
        windows: `del backend/src/database/kira.db`
        mac: `rm backend/src/database/kira.db`
    b. rerun table creation 
        `python -m database.db_setup_tables`

### Take note that the files in `.gitignore` are *NOT* to be pushed into git (venv, kira.db etc.)


