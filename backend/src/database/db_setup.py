from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

#/.../backend/src/database
SRC_DIR = Path(__file__).resolve().parent
DB_PATH = SRC_DIR / "kira.db" 
ECHO = os.getenv("DB_ECHO", "0") == "1"

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=ECHO,
    connect_args={"check_same_thread": False},  
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)
Base = declarative_base()
