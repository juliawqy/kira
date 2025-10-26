import threading
import socket
import time
import uuid
import pytest
import uvicorn

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# DB / app imports (adjusted to your project structure)
from backend.src.database.db_setup import Base
import backend.src.database.db_setup as db_setup
import backend.src.services.user as user_service
import backend.src.services.task as task_service
import backend.src.services.comment as comment_service
import backend.src.services.project as project_service
from backend.src.main import app


@pytest.fixture(scope="module")
def driver():
    options = Options()
    # options.add_argument("--headless=new")  # uncomment for CI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    yield driver
    try:
        driver.quit()
    except Exception:
        pass