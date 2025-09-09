from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# create local database in project root folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "kira.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)