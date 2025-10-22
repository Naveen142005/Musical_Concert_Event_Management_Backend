# create_tables.py
from app.database.connection import Base, engine
from app.models.user import User
from app.models.role import Role  

Base.metadata.create_all(bind=engine)
