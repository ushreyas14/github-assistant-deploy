from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGODB_URI

client = AsyncIOMotorClient(MONGODB_URI)

db = client.github_rag

chunks_collection = db.chunks

repositories_collection = db.repositories

query_logs_collection = db.query_logs

evaluations_collection = db.evaluations