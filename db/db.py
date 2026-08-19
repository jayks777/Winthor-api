from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
import os

load_dotenv()

DATABASE_URL = URL.create(
    drivername="oracle+oracledb",
    username=os.getenv("DATABASE_USER"),
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_HOST"),
    port=int(os.getenv("DATABASE_PORT")),
    query={
        "service_name": os.getenv("DATABASE_SERVICE")
    }
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False ,bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()