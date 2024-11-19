from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymongo
from bson import ObjectId  # Thêm bson để xử lý ObjectId
import os

app = FastAPI()

# Connect to MongoDB Atlas
mongo_url = os.environ.get('MONGO_URL')
database_name = os.environ.get('DATABASE_NAME')

if not mongo_url or not database_name:
    raise ValueError("Environment variables MONGO_URL and DATABASE_NAME must be set")

client = pymongo.MongoClient(mongo_url)
db = client[database_name]

class Challenge(BaseModel):
    description: str
    difficulty_level: str
    scoring_criteria: str

@app.post("/challenges/")
async def create_challenge(challenge: Challenge):
    challenge_data = challenge.dict()
    result = db.challenges.insert_one(challenge_data)
    return {"message": "Challenge created successfully", "challenge_id": str(result.inserted_id)}

@app.get("/challenges/")
async def get_challenges():
    challenges = list(db.challenges.find({}, {"_id": 0}))
    return challenges

@app.put("/challenges/{challenge_id}")
async def update_challenge(challenge_id: str, challenge: Challenge):
    try:
        object_id = ObjectId(challenge_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid challenge ID format")
    
    result = db.challenges.update_one({"_id": object_id}, {"$set": challenge.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return {"message": "Challenge updated successfully"}

@app.delete("/challenges/{challenge_id}")
async def delete_challenge(challenge_id: str):
    try:
        object_id = ObjectId(challenge_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid challenge ID format")
    
    result = db.challenges.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return {"message": "Challenge deleted successfully"}
