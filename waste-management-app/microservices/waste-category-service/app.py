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

# Định nghĩa mô hình WasteCategory
class WasteCategory(BaseModel):
    name: str
    description: str
    disposal_guidelines: str

@app.post("/waste-categories/")
async def create_waste_category(category: WasteCategory):
    category_data = category.dict()
    result = db.waste_categories.insert_one(category_data)
    return {"message": "Category created successfully", "category_id": str(result.inserted_id)}

@app.get("/waste-categories/")
async def get_categories():
    categories = list(db.waste_categories.find({}))
    # Chuyển đổi ObjectId sang chuỗi cho mỗi category
    for category in categories:
        category["_id"] = str(category["_id"])
    return categories

@app.put("/waste-categories/{category_id}")
async def update_category(category_id: str, category: WasteCategory):
    try:
        object_id = ObjectId(category_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid category ID format")

    result = db.waste_categories.update_one({"_id": object_id}, {"$set": category.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category updated successfully"}

@app.delete("/waste-categories/{category_id}")
async def delete_category(category_id: str):
    try:
        object_id = ObjectId(category_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid category ID format")

    result = db.waste_categories.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}
