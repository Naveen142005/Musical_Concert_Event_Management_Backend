# app/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient



client: AsyncIOMotorClient = AsyncIOMotorClient(
    "mongodb://localhost:27017",
    serverSelectionTimeoutMS=5000
)



db = client['Mongo_testing']
col = db['Mongo_test']

