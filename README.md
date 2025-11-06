# KIRA
Repository link: https://github.com/juliawqy/kira/


## How to set up Kira

1. Create local virtual environment
   `python -m venv venv`

2. Activate local environment
   Windows: `venv\Scripts\activate`
   macOS: `source venv/bin/activate`

3. Install dependencies
   `pip install -r requirements.txt`

Repeat steps 1-3 to create virtual enviroments in 3 separate terminals (1 for backend, 1 for frontend, 1 for testing)


### How to set up backend (first terminal)

1. Initialize database with sample data
   `python init_db.py`

2. Run backend project
   `python -m uvicorn backend.src.main:app --reload`
   Access swagger docs: http://localhost:8000/docs

To remove database:
   Windows: `del backend\src\database\kira.db`
   macOS: `rm backend/src/database/kira.db`


### How to set up frontend (second terminal)

1. Install frontend dependencies
   `cd frontend && npm install`

2. Start frontend
   `npm start`

   Access frontend: http://localhost:3000


### Testing (third terminal)

To route notification emails to a fixed test inbox during local runs, set these environment variables before running tests or starting the app.

   Windows (PowerShell):
  `$env:TEST_RECIPIENT_EMAIL = "kirahoora@gmail.com"; $env:TEST_RECIPIENT_NAME = "Kira Local"`
   macOS/Linux (bash/zsh):
  `export TEST_RECIPIENT_EMAIL = "kirahoora@gmail.com"; export TEST_RECIPIENT_NAME="Kira Local"`

1. Run all backend tests
   `pytest`

2. Run only backend unit tests
   `pytest tests/backend/unit`

3. Run only backend integration tests
   `pytest tests/backend/integration`

4. Run full-stack e2e tests
   `pytest tests/e2e`

Check tests status on HTML page

   Windows: `start htmlcov\index.html`
   macOS: `open htmlcov/index.html`
