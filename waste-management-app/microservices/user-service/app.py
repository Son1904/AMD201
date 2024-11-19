from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymongo
from bson import ObjectId  # Import để xử lý ObjectId của MongoDB
import os

app = FastAPI()

# Connect to MongoDB Atlas
mongo_url = os.environ.get('MONGO_URL')
database_name = os.environ.get('DATABASE_NAME')

if not mongo_url or not database_name:
    raise ValueError("Environment variables MONGO_URL and DATABASE_NAME must be set")

client = pymongo.MongoClient(mongo_url)
db = client[database_name]

# Định nghĩa mô hình User
class User(BaseModel):
    name: str
    email: str
    password: str

@app.post("/users/")
async def create_user(user: User):
    user_data = user.dict()
    result = db.users.insert_one(user_data)
    return {"message": "User created successfully", "user_id": str(result.inserted_id)}

@app.get("/users/")
async def get_users():
    users = list(db.users.find({}, {"_id": 1, "name": 1, "email": 1}))
    # Chuyển đổi ObjectId sang chuỗi cho mỗi user
    for user in users:
        user["_id"] = str(user["_id"])
    return users

@app.put("/users/{user_id}")
async def update_user(user_id: str, user: User):
    try:
        object_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    result = db.users.update_one({"_id": object_id}, {"$set": user.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}

@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    try:
        object_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    result = db.users.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
