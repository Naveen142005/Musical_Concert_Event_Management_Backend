# app/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient



client: AsyncIOMotorClient = AsyncIOMotorClient(
    "mongodb://localhost:27017",
    serverSelectionTimeoutMS=5000
)

db = client['EMS']
col = db['facility_selected_log']
content = db["Content_Management"]

