
from app.database.connection import SessionLocal
class db:
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

DB = db()