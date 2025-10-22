# KIRA

## How to set up local kira.db
1. create local virtual environment 
    `python -m venv venv`

2. activate local environment
    windows: `venv\Scripts\activate`
    mac: `source venv/bin/activate`

3. install dependencies 
    `pip install -r requirements.txt`

4. Create database and setup tables (SQLite)
    `python -m backend.src.database.db_setup_tables`

5. run project 
    `uvicorn backend.src.main:app --reload`
    Access swagger docs: http://localhost:8000/docs

6. if you modify table structure (like `Task`), 
    a. delete old database
        windows: `del backend\src\database\kira.db`
        mac: `rm backend/src/database/kira.db`
    b. rerun table creation 
        `python -m backend.src.database.db_setup_tables`

### Take note that the files in `.gitignore` are *NOT* to be pushed into git (venv, kira.db etc.)


## Testing
### Run all backend tests
pytest

### Run only backend unit tests
pytest tests/backend/unit

### Run only backend integration tests
pytest tests/backend/integration

### Run full-stack e2e tests
pytest tests/e2e

### Run all frontend tests
cd frontend && npm test

### Run only unit tests
cd frontend && npm run test:unit

### Run only integration tests
cd frontend && npm run test:integration

### Run frontend E2E tests (browser-based)
cd frontend && npm run test:e2e

### Check tests status on HTML page
    windows: start htmlcov\index.html
    mac: open htmlcov/index.html

`