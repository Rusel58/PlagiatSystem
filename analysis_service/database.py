import os
from sqlalchemy import create_engine, Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://kpo_user:kpo_pass@postgres:5432/kpo_db"
)

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class AnalysisResult(Base):
    __tablename__ = "results"
    file_id = Column(String, primary_key=True, index=True)
    paragraphs = Column(Integer)
    words = Column(Integer)
    characters = Column(Integer)
    wordcloud_loc = Column(String, nullable=True)

def init_db(retries: int = 10, delay: int = 2):
    """
    Пытаемся создать таблицы, пока Postgres не будет готов.
    retries — число попыток, delay — пауза между ними в секундах.
    """
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ DB initialized")
            return
        except OperationalError as e:
            print(f"⚠️  DB unavailable (attempt {attempt}/{retries}), retrying in {delay}s…")
            time.sleep(delay)
    # Если не удалось после всех попыток — аварийно выходим
    raise RuntimeError("❌ Could not connect to the database after multiple retries")
