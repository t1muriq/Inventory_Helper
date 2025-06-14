from application.database import init_db
from application import db_models

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")