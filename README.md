# KIRA

## How to set up local kira.db

1. create local virtual environment
   `python -m venv venv`

2. activate local environment
   windows: `venv\Scripts\activate`
   mac: `source venv/bin/activate`

3. install dependencies
   `pip install -r requirements.txt`

4. Initialize database with sample data (SQLite)
   `python init_db.py`

   This will create all tables and seed initial test data including:

   - Users: Cong, Julia (Staff), Manager1, Director1
   - Projects: Project Alpha, Project Beta
   - Tasks assigned to users with various statuses
   - Comments on tasks

   Note: If you need to reset the database, delete `backend/src/database/kira.db` first

5. Run backend project
   `python -m uvicorn backend.src.main:app --reload`
   Access swagger docs: http://localhost:8000/docs

6. Install frontend dependencies and run frontend (in a separate terminal)
   `cd frontend && npm install`
   `npm start`

   Access frontend: http://localhost:3000

7. If you modify table structure (like `Task`),
   a. delete old database
   windows: `del backend\src\database\kira.db`
   mac: `rm backend/src/database/kira.db`
   b. rerun database initialization
   `python init_db.py`

### Take note that the files in `.gitignore` are _NOT_ to be pushed into git (venv, kira.db etc.)

## Default Test Accounts

After running `init_db.py`, you can use these test accounts:

**Staff Users:**

- Cong: `cong@example.com` / `Password123!`
- Julia: `julia@example.com` / `Password123!`

**Administrative Users:**

- Manager1: `manager@example.com` / `Password123!`
- Director1: `director@example.com` / `Password123!`

## Testing

### Run all backend tests

pytest

### Run only backend unit tests

pytest tests/backend/unit

### Run only backend integration tests

pytest tests/backend/integration

### See test email recipient (local)

To route notification emails to a fixed test inbox during local runs, set these environment variables before running tests or starting the app.

- Windows (PowerShell):
  `$env:TEST_RECIPIENT_EMAIL = "kirahoora@gmail.com"; $env:TEST_RECIPIENT_NAME = "Kira Local"`

- macOS/Linux (bash/zsh):
  `export TEST_RECIPIENT_EMAIL="kirahoora@gmail.com"; export TEST_RECIPIENT_NAME="Kira Local"`

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
