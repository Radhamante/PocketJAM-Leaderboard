from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

pg_password = os.environ.get("POSTGRES_PASSWORD")
pg_user = os.environ.get("POSTGRES_USER")
pg_ip = os.environ.get("POSTGRES_IP")
pg_name = os.environ.get("POSTGRES_DB")

DATABASE_URL = f"""postgresql://{pg_user}:{pg_password}@{pg_ip}/{pg_name}"""

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
