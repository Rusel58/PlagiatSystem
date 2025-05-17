import os
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# берём из окружения или по-умолчанию подключаемся к Postgres
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://kpo_user:kpo_pass@postgres:5432/kpo_db"
)

# для sqlite нужен флаг check_same_thread, для Postgres — нет
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class FileMeta(Base):
    __tablename__ = "files"
    file_id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    digest = Column(String, index=True)


def init_db():
    Base.metadata.create_all(bind=engine)
