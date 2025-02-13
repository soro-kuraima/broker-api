# app/init_db.py
from app.database import init_db

if __name__ == "__main__":
    print("Creating initial database...")
    init_db()
    print("Database initialized!")