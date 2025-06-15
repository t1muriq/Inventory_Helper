from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:123@localhost:5435/inventory_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    import data_base.db_models # Импортируем, чтобы модели были зарегистрированы в Base.metadata
    print(Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine) 