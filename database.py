from pymongo import AsyncMongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncMongoClient(MONGO_URI)
db = client["ai_job_assist"]

users_collection = db["users"]
resumes_collection = db["resumes"]
outputs_collection = db["outputs"]

async def ping_db():
    try:
        await client.admin.command("ping")
        print("MongoDB connected successfully")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")